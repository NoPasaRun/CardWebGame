from wtforms import StringField, IntegerField  # classes describing fields in forms
from wtforms.validators import InputRequired, Email, Length  # validators for forms
from flask_wtf import FlaskForm


class SignUpForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(3, 50)])
    password = StringField(validators=[InputRequired(), Length(10)])
    age = IntegerField(validators=[InputRequired()])
    email = StringField(validators=[InputRequired(), Email()])
