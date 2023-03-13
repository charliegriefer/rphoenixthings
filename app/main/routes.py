from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.forms import AddEventForm
from app.main import main_blueprint

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
    cats = sorted(event_categories, key=lambda d: d["title"])
    form.category.choices = [(c.get("value"), f'{c.get("emoji")} {c.get("title")}') for c in cats]
    form.category.choices.append(("[OTHER]", "❓Other"))
    form.category.choices.insert(0, ("", "Choose a Category"))
    if request.method == "POST" and form.validate_on_submit():
        print("GOOD JOB!")
        exit(27)
    return render_template("add_event.html", form=form)
