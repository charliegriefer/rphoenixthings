from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.forms import AddEventForm
from app.main import main_blueprint

event_categories = [
    {"title": "Home & Garden", "value": "[HOME/GARDEN]", "emoji": "๐ "},
    {"title": "Flora", "value": "[FLORA]", "emoji": "๐ต"},
    {"title": "Gaming", "value": "[GAMING]", "emoji": "๐น๏ธ"},
    {"title": "Comedy", "value": "[COMEDY]", "emoji": "๐ค"},
    {"title": "Meetup", "value": "[MEETUP]", "emoji": "๐"},
    {"title": "Community", "value": "[COMMUNITY]", "emoji": "๐"},
    {"title": "Food & Drink", "value": "[FOOD/DRINK]", "emoji": "๐"},
    {"title": "Film/Movies", "value": "[FILM]", "emoji": "๐ฅ"},
    {"title": "Music", "value": "[MUSIC]", "emoji": "๐ต"},
    {"title": "Sports", "value": "[SPORTS]", "emoji": "๐"},
    {"title": "Theater", "value": "[THEATER]", "emoji": "๐ญ"},
    {"title": "Fairs and Festivals", "value": "[FAIRS/FESTIVALS]", "emoji": "๐ก"},
    {"title": "Dance", "value": "[DANCE]", "emoji": "๐บ"},
    {"title": "Aliens", "value": "[ALIENS]", "emoji": "๐ฝ"},
    {"title": "Pets", "value": "[PETS]", "emoji": "๐น"},
    {"title": "Cars", "value": "[CARS]", "emoji": " ๐"},
    {"title": "Market", "value": "[MARKET]", "emoji": "๐"},
    {"title": "Art", "value": "[ART]", "emoji": "๐จ"},
    {"title": "Kids/Family", "value": "[KIDS/FAMILY]", "emoji": "๐ช"},
    {"title": "Books/Reading", "value": "[BOOKS/READING]", "emoji": "๐"},
    {"title": "Science and Stuff", "value": "[SCIENCE/STUFF]", "emoji": "๐งช"},
    {"title": "Health/Wellness", "value": "[HEALTH]", "emoji": "โค๏ธ"},
    {"title": "Tech", "value": "[TECH]", "emoji": "๐ฅ๏ธ"},
    {"title": "Podcast", "value": "[PODCAST]", "emoji": "๐๏ธ"},
    {"title": "Trivia", "value": "[TRIVIA]", "emoji": "โ"},
    {"title": "Winter Festivities", "value": "[WINTER FESTIVITIES]", "emoji": "โ๏ธ"},
    {"title": "Fall Festivities", "value": "[FALL FESTIVITIES]", "emoji": "๐"},
    {"title": "Holidays/Halloween", "value": "[HOLIDAYS/HALLOWEEN]", "emoji": "๐ป"},
    {"title": "Holidays/July 4th", "value": "[HOLIDAYS/JULY4TH]", "emoji": "๐"},
    {"title": "Holidays/Easter", "value": "[HOLIDAYS/EASTER]", "emoji": "๐ฐ"},
    {"title": "Holidays/Mother's Day", "value": "[HOLIDAYS/MOTHERS DAY]", "emoji": "๐ฉ"},
    {"title": "Holidays/Christmas", "value": "[HOLIDAYS/XMAS]", "emoji": "๐"},
    {"title": "Holidays/New Year's Eve", "value": "[HOLIDAYS/NEW YEAR'S EVE]", "emoji": "๐"},
    {"title": "Holidays/St. Patrick's Day", "value": "[HOLIDAYS/ST PAT'S]", "emoji": "โ๏ธ"}
]

# {"title": "Other", "value": "[OTHER]": "emoji": "โ"}


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
    form.category.choices.append(("[OTHER]", "โOther"))
    form.category.choices.insert(0, ("", "Choose a Category"))
    if request.method == "POST" and form.validate_on_submit():
        print("GOOD JOB!")
        exit(27)
    return render_template("add_event.html", form=form)
