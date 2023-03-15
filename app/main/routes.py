import os
import re
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.forms import AddEventForm, ListEventsForm
from app.main import main_blueprint

CAL_ID = os.environ["CALENDAR_ID"]
CAL_URL = f"https://calendar.google.com/calendar/embed?src={CAL_ID}&ctz=America%2FPhoenix&mode=AGENDA"
CAL_API_KEY = os.environ["CALENDAR_API_KEY"]
SCOPES = ["https://www.googleapis.com/auth/calendar"]

event_categories = [
    {"title": "Home & Garden", "value": "[HOME/GARDEN]", "emoji": "🏠"},
    {"title": "Flora", "value": "[FLORA]", "emoji": "🌵"},
    {"title": "Gaming", "value": "[GAMING]", "emoji": "🕹️"},
    {"title": "Comedy", "value": "[COMEDY]", "emoji": "🎤"},
    {"title": "Meetup", "value": "[MEETUP]", "emoji": "📛"},
    {"title": "Community", "value": "[COMMUNITY]", "emoji": "📛"},
    {"title": "Food & Drink", "value": "[FOOD/DRINK]", "emoji": "🍔"},
    {"title": "Film/Movies", "value": "[FILM]", "emoji": "🎥"},
    {"title": "Music", "value": "[MUSIC]", "emoji": "🎵"},
    {"title": "Sports", "value": "[SPORTS]", "emoji": "🏆"},
    {"title": "Theater", "value": "[THEATER]", "emoji": "🎭"},
    {"title": "Fairs and Festivals", "value": "[FAIRS/FESTIVALS]", "emoji": "🎡"},
    {"title": "Dance", "value": "[DANCE]", "emoji": "🕺"},
    {"title": "Aliens", "value": "[ALIENS]", "emoji": "👽"},
    {"title": "Pets", "value": "[PETS]", "emoji": "🐹"},
    {"title": "Cars", "value": "[CARS]", "emoji": " 🚘"},
    {"title": "Market", "value": "[MARKET]", "emoji": "🛒"},
    {"title": "Art", "value": "[ART]", "emoji": "🎨"},
    {"title": "Kids/Family", "value": "[KIDS/FAMILY]", "emoji": "👪"},
    {"title": "Books/Reading", "value": "[BOOKS/READING]", "emoji": "📖"},
    {"title": "Science and Stuff", "value": "[SCIENCE/STUFF]", "emoji": "🧪"},
    {"title": "Health/Wellness", "value": "[HEALTH]", "emoji": "❤️"},
    {"title": "Tech", "value": "[TECH]", "emoji": "🖥️"},
    {"title": "Podcast", "value": "[PODCAST]", "emoji": "🎙️"},
    {"title": "Trivia", "value": "[TRIVIA]", "emoji": "❓"},
    {"title": "Winter Festivities", "value": "[WINTER FESTIVITIES]", "emoji": "❄️"},
    {"title": "Fall Festivities", "value": "[FALL FESTIVITIES]", "emoji": "🍂"},
    {"title": "Holidays/Halloween", "value": "[HOLIDAYS/HALLOWEEN]", "emoji": "👻"},
    {"title": "Holidays/July 4th", "value": "[HOLIDAYS/JULY4TH]", "emoji": "🎆"},
    {"title": "Holidays/Easter", "value": "[HOLIDAYS/EASTER]", "emoji": "🐰"},
    {"title": "Holidays/Mother's Day", "value": "[HOLIDAYS/MOTHERS DAY]", "emoji": "👩"},
    {"title": "Holidays/Christmas", "value": "[HOLIDAYS/XMAS]", "emoji": "🎄"},
    {"title": "Holidays/New Year's Eve", "value": "[HOLIDAYS/NEW YEAR'S EVE]", "emoji": "🎉"},
    {"title": "Holidays/St. Patrick's Day", "value": "[HOLIDAYS/ST PAT'S]", "emoji": "☘️"}
]
# {"title": "Other", "value": "[OTHER]": "emoji": "❓"}


@main_blueprint.route("/")
@main_blueprint.route("/index")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    return redirect(url_for("auth.login"))


@main_blueprint.route("/home", endpoint="home")
@login_required
def home():
    return render_template("home.html")


@main_blueprint.route("/add_event", endpoint="add_event", methods=["GET", "POST"])
@login_required
def add_event():
    form = AddEventForm()

    populate_cats(form)

    if request.method == "POST" and form.validate_on_submit():
        creds = get_creds()
        try:
            service = build("calendar", "v3", credentials=creds)

            description = ""
            if form.link.data:
                description += f"[link: {form.link.data}]\n"
            if form.cost.data:
                description += f"[cost: {form.cost.data}]\n"
            if form.details.data:
                description += f"[details: {form.details.data}]\n"

            location = ", ".join([form.venueName.data, form.venueAddress.data])

            event_data = {
                "summary": f"{form.category.data} {form.title.data}",
                "location": location,
                "description": description,
                "start": {
                    "dateTime": f"{form.eventDate.data}T{form.eventTime.data}-07:00",
                    "timeZone": "America/Phoenix",
                },
                "end": {
                    "dateTime": f"{form.eventDate.data}T{form.eventTime.data}-07:00",
                    "timeZone": "America/Phoenix",
                },
            }

            service.events().insert(calendarId=CAL_ID, body=event_data).execute()

        except HttpError as error:
            print(f"An error occurred: {error}")

        else:
            flash("The event has been added.", "success")
            return redirect(url_for("main.home"))

    return render_template("add_event.html", form=form)


@main_blueprint.route("/list_events", endpoint="list_events", methods=["GET", "POST"])
@login_required
def list_events():
    form = ListEventsForm()
    if request.method == "POST" and form.validate_on_submit():
        creds = get_creds()
        service = build("calendar", "v3", credentials=creds)
        sd = f"{form.start_date.data}T{time.min}-07:00"
        ed = f"{form.start_date.data + timedelta(days=6)}T{time.max}-07:00"

        cal_events = service.events().list(calendarId=CAL_ID,
                                           timeMin=sd,
                                           timeMax=ed,
                                           singleEvents=True,
                                           orderBy="startTime").execute()
        items = cal_events.get("items")

        events = []
        for e in items:
            event = Event(summary=e.get("summary"),
                          start=e.get("start"),
                          location=e.get("location"),
                          description=e.get("description"))

            # check to see if we have this event (summary/date/location)
            result = [d for d in events if (d.category == event.category and
                                            d.title == event.title and
                                            d.event_date == event.event_date and
                                            d.location == event.location)]
            if result:
                result[0].event_time.append(event.event_time[0])
            else:
                events.append(event)

        dates = _get_dates_in_week(events)

        events_text = _get_post_intro(datetime.strptime(sd[:19], "%Y-%m-%dT%H:%M:%S"),
                                      datetime.strptime(ed[:19], "%Y-%m-%dT%H:%M:%S"))
        events_text += "\n\n"

        for event_date in dates:
            nt_url = f"https://www.phoenixnewtimes.com/calendar?dateRange[]={event_date.strftime('%Y-%m-%d')}"
            events_text += f"**[{event_date.strftime('%A')} {event_date.strftime('%B %d')}]({nt_url})**\n\n"

            daily_events = sorted(list(filter(lambda _: _.event_date == event_date, events)),
                                  key=lambda x: x.event_time[0])
            categories_today = _get_categories(daily_events)

            for category in categories_today:

                ec = [q for q in event_categories if q.get("value") == category][0]

                events_text += f"* {ec.get('emoji')} _{ec.get('title')}_ \n"
                events_by_category = filter(lambda _: _.category == category, daily_events)

                for current_event in events_by_category:
                    if current_event.link:
                        events_text += f"    * [{current_event.title.strip()}]({current_event.link})"
                    else:
                        events_text += f"    * {current_event.title.strip()}"

                    if current_event.venue:
                        venue = f": {current_event.venue}[📍](https://maps.google.com/?q={current_event.location})"
                        events_text += f"{venue}, {current_event.city} "

                    list_of_times = ", ".join(
                        list(map(lambda x: x.strftime("%-I:%M%p"), sorted(current_event.event_time))))
                    events_text += list_of_times
                    if current_event.cost:
                        events_text += f" _({current_event.cost})_"
                    if current_event.details:
                        events_text += f"  \n    *{current_event.details}*"

                    events_text += "\n\n"

        return render_template("events_text.html",
                               events_text=events_text,
                               start_date=datetime.strptime(sd[:19], "%Y-%m-%dT%H:%M:%S"),
                               end_date=datetime.strptime(ed[:19], "%Y-%m-%dT%H:%M:%S"))

    return render_template("list_events.html", form=form)


# --------------------------------------------------------------------------------------------------------------------


def populate_cats(form: AddEventForm) -> None:
    cats = sorted(event_categories, key=lambda d: d["title"])
    form.category.choices = [(c.get("value"), f'{c.get("emoji")} {c.get("title")}') for c in cats]
    form.category.choices.append(("[OTHER]", "❓Other"))
    form.category.choices.insert(0, ("", "Choose a Category"))


def get_creds() -> Credentials:
    creds = None
    if os.path.exists(f"{current_app.root_path}/token.json"):
        creds = Credentials.from_authorized_user_file(f"{current_app.root_path}/token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(f"{current_app.root_path}/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f"{current_app.root_path}token.json", "w") as token:
            token.write(creds.to_json())

    return creds


class Event:
    def __init__(self,
                 summary: str,
                 start: Dict[str, str],
                 location: str,
                 description: str):
        self.category: str = self.set_category(summary)
        self.title: str = self.set_title(summary)
        self.event_date: date = self.get_event_date(start.get("dateTime"))
        self.event_time: List[time] = self.get_event_time(start.get("dateTime"))
        self.link: str = self.get_link(description)
        self.cost: str = self.get_cost(description)
        self.details: str = self.get_details(description)
        self.location: str = location
        self.venue: str = None if location is None else self.get_venue(location)
        self.city: str = None if location is None else self.get_city(location)

    @staticmethod
    def set_category(summary) -> Optional[str]:
        cat = re.search("^.*]", summary)
        if cat:
            return cat.group()
        else:
            return None

    @staticmethod
    def set_title(summary) -> Optional[str]:
        matches = re.search("]\s(.*$)", summary)
        if matches:
            return matches.group(1)
        else:
            return None

    @staticmethod
    def get_date_time(start: str):
        dt = datetime.strptime(start[:19], "%Y-%m-%dT%H:%M:%S")
        event_date = dt.date()
        event_time = dt.time()
        return event_date, event_time

    def get_event_date(self, start: str) -> date:
        return self.get_date_time(start)[0]

    def get_event_time(self, start: str) -> list[time]:
        return [self.get_date_time(start)[-1]]

    @staticmethod
    def get_link(description: str) -> Optional[str]:
        description = description.replace(u"\xa0", u" ")
        description = re.sub("<[^<]+?>", "", description)  # remove html

        matches = re.search("\[link:\s*(\S*)]", description)
        if matches:
            return matches.group(1)
        else:
            return None

    @staticmethod
    def get_cost(description: str) -> Optional[str]:
        description = description.replace(u"\xa0", u" ")
        description = re.sub("<[^<]+?>", "", description)  # remove html

        matches = re.search("\[cost:\s*(.*?)]", description)
        if matches:
            cost = matches.group(1)
            return cost.replace("free", "FREE")
        else:
            return None

    @staticmethod
    def get_details(description: str) -> Optional[str]:
        description = description.replace(u"\xa0", u" ")

        matches = re.search("\[details:\s*(.*?)]", description)
        if matches:
            details = matches.group(1)
            return re.sub("<[^<]+?>", "", details)
        else:
            return None

    @staticmethod
    def get_venue(location: str) -> Optional[str]:
        if location:
            return location.split(",")[0]
        else:
            return None

    @staticmethod
    def get_city(location: str) -> Optional[str]:
        matches = re.search(r"([\w\s]*), AZ", location)
        if matches:
            return matches.group(1).strip()
        else:
            return None


def _get_dates_in_week(events: List[Event]) -> List[date]:
    """ given a list of events, returns a list of unique dates (sorted). """
    dates = list(set([e.event_date for e in events]))
    dates.sort()
    return dates


def _get_categories(events: List[Event]) -> List[str]:
    """ given a list of events, returns a list of unique categories (sorted). """
    categories = list(set([e.category for e in events]))
    categories.sort()
    return categories


def _get_post_intro(start_date: date, end_date: date) -> str:
    sd = start_date.strftime("%B %d")
    ed = end_date.strftime("%B %d")

    intro = (f"Week of: **{sd}** - **{ed}**\n\n"
             "This is a weekly thread of some of the goings-on in and around the Phoenix metro area. "
             f"Feel free to subscribe to our public [Google Calendar]({CAL_URL}) "
             "of meetups and events as well. "
             "\n\n"
             "If there is an event that you don't see posted here, please add a comment below. "
             "In the comment, include the event, date, time, cost (if any), location, and a brief description. "
             "Please upvote people who share good/interesting events, even if it may not be something you will attend. "
             "Don't see anything of interest? Click on any one of the dates to be taken to a comprehensive listing of "
             "events for that day over at the [Phoenix New Times' web site](https://www.phoenixnewtimes.com/calendar). "
             "\n\n"
             "If you organize or know of a meet-up that you'd like to promote, "
             "please PM the mods and we'll look into getting it added to the calendar. "
             "We'll post these events up to six weeks out. At that point, we ask that you ping us again. "
             "This just helps to ensure that the events stay fresh and no defunct events appear on the calendar. "
             "\n\n"
             "Please take the time to verify the date, time, location, and cost of an event before you head out. "
             "\n\n"
             "----")

    return intro
