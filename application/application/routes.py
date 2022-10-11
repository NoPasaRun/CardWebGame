import os
from typing import Dict, Union

from flask import Flask, request, redirect, render_template, session
from flask_wtf import CSRFProtect
from forms import SignUpForm
from flask_login import LoginManager, login_required, logout_user, login_user

from login_view import LoginUser
from application.application.models import User, Base
from application.application.database import db_session
from application.application.game import GameSession, LobbySession, Attacker, Defender, Player

app = Flask(__name__, template_folder="../templates", static_folder="../static")
SECRET_KEY = os.urandom(32)

app.config['SECRET_KEY'] = SECRET_KEY
app.config["CSRF_PROTECT"] = False
app.jinja_env.filters['zip'] = zip

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id: int):
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
    return render_template("admin.html")


@app.route("/sign_up/", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()
    if request.method == "GET":
        return render_template("sign_up.html", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            data = form.data
            user = User(username=data["username"])
            user.set_password(data["password"])
            db_session.add(user)
            db_session.commit()
            return redirect("/login/")
        return form.errors, 404


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        user = User.get_by_username(request.form["username"])
        if user and user.check_password(request.form["password"]):
            userlogin = LoginUser().create(user)
            login_user(userlogin)
            return redirect("/")
        return "Password or username is not valid", 400


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect("/login/")


@app.route('/game_lobby/<int:lobby_id>/', methods=["GET", "POST"])
@login_required
def lobby(lobby_id: int):
    lobby_session = LobbySession(lobby_index=lobby_id)
    if lobby_session.game_status:
        return redirect(f"/game/{lobby_id}/")
    if request.method == "GET":
        user: User = User.get(session["_user_id"])
        lobby_session.add_user(user)
        return render_template("lobby.html", lobby=lobby_session, user=user)
    elif request.method == "POST":
        lobby_session.game_status = True
        GameSession(user_data=lobby_session.users, game_index=lobby_id)
        return redirect(f"/game/{lobby_id}/")


@app.route('/game/<int:game_id>/', methods=["GET", "POST"])
@login_required
def game(game_id: int):
    game_ses: GameSession = GameSession.get_game(game_id)
    lobby_ses: LobbySession = LobbySession(game_id)

    user: User = User.get(int(session.get("_user_id")))
    requested_player: Player = game_ses.get_player_by_user(user)

    context: Dict = {"user": user, "lobby": lobby_ses, "game": game_ses, "pair": game_ses.pair}
    if game_ses:
        if requested_player in game_ses.players:
            if request.method == "GET":
                return render_template("lobby.html", **context)
            elif request.method == "POST":
                context.pop("lobby")
                return render_template("game.html", **context)
        return "You are not a part of this game"
    return "Game not found!"


@app.route('/game/<int:game_id>/make_move', methods=["POST"])
@login_required
def make_move(game_id: int):
    game_ses: GameSession = GameSession.get_game(game_id)
    user: User = User.get(int(session.get("_user_id")))
    current_player: Union[Attacker, Defender] = game_ses.pair.get_current_player(game_ses)
    data = request.form.to_dict()

    if user == current_player:
        card_value: str = data.get("card_value")
        table_id: str = data.get("table_id")

        success = current_player.go_on(card_value, game_ses.pair.table, int(table_id))
        if success:
            message = "Ok!"
        else:
            message = "Your card is lower than attacker's card or you tried to cheat"
    else:
        message = "That is not your turn"
    context: Dict = {"user": user, "game": game_ses, "pair": game_ses.pair, "message": message}
    return render_template("game.html", **context)


@app.route('/game/<int:game_id>/change_status', methods=["POST"])
@login_required
def change_status(game_id: int):
    game_ses: GameSession = GameSession.get_game(game_id)
    user: User = User.get(int(session.get("_user_id")))

    attacker: Attacker = game_ses.pair.attacker
    defender: Defender = game_ses.pair.defender
    if user == attacker:
        attacker.is_awaken = not attacker.is_awaken
    elif user == defender:
        defender.is_awaken = not defender.is_awaken


if __name__ == '__main__':
    Base.metadata.create_all()
    csrf = CSRFProtect(app)
    csrf.init_app(app)
    app.run(host="0.0.0.0", port=8000, debug=True)
