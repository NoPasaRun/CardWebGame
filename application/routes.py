from flask import Flask, send_from_directory, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from application.models import create_db, User, Group
from application.settings import static_folder
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, login_user, login_required, logout_user
import os


app = Flask(__name__, template_folder='templates')
csrf = CSRFProtect(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class LoginUser(LoginManager):

    def fromDB(self, user_id):
        self.__user = User.get(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user.id)


class SignUpForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(3, 50)])
    password = StringField(validators=[InputRequired(), Length(10)])
    age = IntegerField(validators=[InputRequired()])
    email = StringField(validators=[InputRequired(), Email()])


@login_manager.user_loader
def load_user(user_id):
    return LoginUser().fromDB(user_id)


@app.route("/", methods=["GET"])
@login_required
def main():
    return render_template("index.html")


@app.route("/admin/", methods=["GET"])
@login_required
def admin():
    user = User.get(session["_user_id"])
    group = Group.get(user.group_id)
    if group.title == "advanced":
        return render_template("admin.html")
    return "You have no rights", 401


@app.route("/static/<path:static_file>/", methods=["GET"])
def send_static(static_file):
    return send_from_directory(static_folder, static_file)


@app.route("/sign_up/", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()
    if request.method == "GET":
        return render_template("sign_up.html", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            data = form.data
            data.pop("csrf_token")
            User(**data).save()
            return redirect("/login/")
        return form.errors, 404


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        user = User.get_by_username(request.form["username"])
        if user and check_password_hash(user.password, request.form["password"]):
            userlogin = LoginUser().create(user)
            login_user(userlogin)
            return redirect("/")
        return "Password or username is not valid", 400


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect("/login/")


if __name__ == '__main__':
    create_db(create_superuser=True)
    csrf.init_app(app)
    app.run(host="0.0.0.0", port=8000)
