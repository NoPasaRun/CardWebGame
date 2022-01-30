from flask import Flask, send_from_directory, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from application.models import create_db, User, Group
from application.settings import static_folder
from application.game import Game
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, login_user, login_required, logout_user
import threading
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
def main():
    user = session.get("_user_id", False)
    if user:
        is_authenticated = True
    else:
        is_authenticated = False
    return render_template("index.html", is_auth=is_authenticated)


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
            output = User(**data).save()
            if output["status_code"].startswith("4"):
                return output["message"], output["status_code"]
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


@app.route('/game/<int:game_id>/', methods=["GET", "POST"])
@login_required
def game(game_id):
    user = User.get(session["_user_id"])
    user = {"id": user.id, "username": user.username, "age": user.age}
    return_to_post = False
    if request.method == "GET":
        if Game.exist(game_id):
            game_ses = Game.get(game_id)
            if game_ses.start:
                if user["id"] not in [player.player_id for player in game_ses.players]:
                    return "Game has already started", 400
            else:
                if user["id"] not in [player.player_id for player in game_ses.players]:
                    if len(game_ses.players) == 6:
                        return "The game is full of people", 400
                    game_ses.add_player(user)
            i_player, *_ = [i_player for i_player in game_ses.players if i_player.player_id == user["id"]]
            return render_template("game.html", game=game_ses, i_player=i_player)
        else:
            Game(game_id, user)
            return redirect(f"/game/{game_id}/")
    if request.method == "POST" or return_to_post:
        game_ses = Game.get(game_id)
        i_player, *_ = [i_player for i_player in game_ses.players if i_player.player_id == user["id"]]
        if request.form.get("start-game", False):
            if Game.exist(game_id):
                if user["id"] == game_ses.creator["id"]:
                    game_ses.start = True
                    game_ses.initialize_game()
                    return redirect(f"/game/{game_id}/")
                else:
                    return "You have no rights", 300
            else:
                return "This game is not existing", 400
        if request.form.get("update-cards", False):
            if Game.exist(game_id):
                player_id = request.form.get
                cards = request.form.get("update-cards")
                game_ses.update_player_cards(player_id, cards)
        if request.form.get("update-table", False):
            if Game.exist(game_id):
                value_of_card = request.form.get("card")
                place_id = request.form.get("place_id")
                game_ses.fill_table(i_player=i_player, place_id=place_id, value_of_card=value_of_card)
        if request.form.get("update-page", False):
            if Game.exist(game_id):
                return render_template("game-info.html", game=game_ses, i_player=i_player)


if __name__ == '__main__':
    test = True
    if test:
        game = Game(1, {"id": 1, "username": "NoPasaRan", "age": 16})
        [game.add_player({"id": i, "username": User.get(i).username, "age": User.get(i).age}) for i in range(2, 7)]
    create_db(create_superuser=True)
    csrf.init_app(app)
    app.run(host="0.0.0.0", port=8000)
