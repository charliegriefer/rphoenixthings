import re

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField, DateField, PasswordField, SelectField, StringField, SubmitField, TextAreaField, TimeField, URLField
)
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional, URL, ValidationError

from app.models import User


pw_description = "Password requirements:<ul>"
pw_description += "<li>Must be between 8 and 22 characters.</li>"
pw_description += "<li>Must contain at least one uppercase letter, one lowercase letter, and one digit.</li>"
pw_description += "<li>Spaces are not allowed.</li></ul>"

username_description = "Username requirements:<ul>"
username_description += "<li>Must be between 4 and 24 characters.</li>"
username_description += "<li>Valid special characters: - _ @ ! ^ * $</li>"
username_description += "<li>Spaces are not allowed.</li></ul>"


class LoginForm(FlaskForm):
    email = StringField("Email Address:", validators=[InputRequired()], render_kw={"placeholder": "Email Address"})
    password = PasswordField("Password:", validators=[InputRequired()], render_kw={"placeholder": "Password"})
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    email = StringField("Email Address:",
                        validators=[InputRequired(), Email()],
                        render_kw={"placeholder": "Email Address"})
    password = PasswordField("Password:",
                             validators=[InputRequired(), Length(min=8, max=24)],
                             render_kw={"placeholder": "Password"},
                             description=pw_description)
    password2 = PasswordField("Repeat Password:",
                              validators=[InputRequired(), EqualTo("password", message="Passwords do not match.")],
                              render_kw={"placeholder": "Repeat Password"})
    submit = SubmitField("Register")

    def validate_password(self, password: StringField) -> None:
        regex = [r"[A-Z]", r"[a-z]", r"[0-9]"]
        is_valid_pw = all(re.search(r, password.data) for r in regex) and not re.search(r"\s", password.data)
        if password.data != self.password and not is_valid_pw:
            raise ValidationError("Password is invalid.")

    def validate_email(self, email: StringField) -> None:
        if email.data != self.email and User.query.filter(User.email == email.data.strip()).first():
            raise ValidationError("Please use a different email address.")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email Address:",
                        validators=[InputRequired(), Email(message="Enter a valid e-mail address.")],
                        render_kw={"placeholder": "E-Mail Address"},)
    submit = SubmitField("Submit")


class AddEventForm(FlaskForm):
    category = SelectField("Category:", validators=[InputRequired()])
    title = StringField("Title:", validators=[InputRequired()])
    eventDate = DateField("Event Date:", validators=[InputRequired()])
    eventTime = TimeField("Event Time:", validators=[InputRequired()])
    venueName = StringField("Venue Name:", validators=[Optional()])
    venueAddress = StringField("Venue Address:", validators=[Optional()])
    cost = StringField("Cost:", validators=[Optional()])
    link = URLField("Link/URL:", validators=[Optional(), URL()])
    details = TextAreaField("Details: ", validators=[Optional()])
    submit = SubmitField("Add Event")
