from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange
from flask_wtf import FlaskForm


class SignUpForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(3, 50)])
    password = StringField(validators=[InputRequired(), Length(10)])


class LobbySessionForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(3, 50)])
    player_count = IntegerField(validators=[NumberRange(2, 6)])
