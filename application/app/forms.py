from wtforms import StringField, IntegerField, ValidationError
from wtforms.validators import InputRequired, Length, NumberRange, EqualTo
from flask_wtf import FlaskForm
from application.app.models import User


class SignUpForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(3, 50)])
    password = StringField(validators=[InputRequired(), Length(10),
                                       EqualTo('password2', message='Passwords must match')])
    password2 = StringField(validators=[InputRequired(), Length(10)])

    def validate_username(self, field):
        if User.get_by_username(field.data):
            raise ValidationError("This username is already exists")


class LobbySessionForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(3, 50)])
    player_count = IntegerField(validators=[NumberRange(2, 6)])
