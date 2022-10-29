from wtforms import StringField
from wtforms.validators import InputRequired, Length
from flask_wtf import FlaskForm


class SignUpForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(3, 50)])
    password = StringField(validators=[InputRequired(), Length(10)])
