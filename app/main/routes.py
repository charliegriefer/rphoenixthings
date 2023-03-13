import os

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.forms import AddEventForm
from app.main import main_blueprint

CAL_ID = "2gerrehdo5ooi1b65ivd5m0vkg@group.calendar.google.com"
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

        try:
            service = build("calendar", "v3", credentials=creds)

            description = ""
            if form.link.data:
                description += f"link: {form.link.data}\n"
            if form.cost.data:
                description += f"cost: {form.cost.data}\n"
            if form.details.data:
                description += f"details: {form.details.data}\n"

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

# --------------------------------------------------------------------------------------------------------------------


def populate_cats(form: AddEventForm) -> None:
    cats = sorted(event_categories, key=lambda d: d["title"])
    form.category.choices = [(c.get("value"), f'{c.get("emoji")} {c.get("title")}') for c in cats]
    form.category.choices.append(("[OTHER]", "❓Other"))
    form.category.choices.insert(0, ("", "Choose a Category"))
