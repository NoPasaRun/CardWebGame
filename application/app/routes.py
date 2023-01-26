from time import time, sleep
from multiprocessing import Process

import json
import logging
from typing import Dict, Union, Tuple, List

from flask import request, redirect, render_template, session
from flask_wtf import CSRFProtect

from application.app.app_config import create_app
from application.app.forms import SignUpForm, LobbySessionForm
from flask_login import LoginManager, login_required, logout_user, login_user

from application.app.login_view import LoginUser
from application.app.models import User, Base
from application.app.database import db_session
from application.app.game import GameSession, LobbySession, Attacker, Defender, Player, Pair


app = create_app()
csrf = CSRFProtect(app)
csrf.init_app(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'


class Timer:

    __all_timers: Dict = {}

    def __init__(self, player: Union[Defender, Attacker], game_ses: GameSession, seconds: int):
        unique_id = player.user_data.id
        timer: Union[Timer, None] = Timer.__all_timers.get(unique_id)
        if isinstance(timer, Timer):
            timer.process.terminate()
        self.player = player
        self.__time, self.__process = self.set_process(game_ses, seconds)
        Timer.__all_timers[unique_id] = self

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, value: int):
        self.__time = value

    @classmethod
    def get_timer_by_player(cls, player: Union[Attacker, Defender], *args) -> Union['Timer', None]:
        unique_id = player.user_data.id
        timer = cls.__all_timers.get(unique_id)
        if timer is None:
            timer = Timer(player, *args)
        return timer

    @property
    def process(self):
        return self.__process

    @process.setter
    def process(self, new_process: Process):
        self.__process = new_process

    def set_process(self, *args) -> Tuple[int, Process]:
        new_process = Process(target=self.tick, args=args)
        new_process.start()
        return int(time()), new_process

    def tick(self, game_ses: GameSession, sec: int):
        sleep(sec)

        index = game_ses.players.index(self.player)
        self.player.is_awaken = False
        self.player = game_ses.players[index]

        game_ses.modified()
        self.time = None


@login_manager.user_loader
def load_user(user_id: int):
    return LoginUser().fromDB(user_id)


def redirect_to_game(func):
    def wrapper(*args, **kwargs):
        game_id = session.get("_game_id")
        if game_id:
            return redirect(f"/game/{game_id}/")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/", methods=["GET"])
@redirect_to_game
def main():
    user = session.get("_user_id")
    if user:
        is_authenticated = True
    else:
        is_authenticated = False
    return render_template("index.html", is_auth=is_authenticated)


@app.route("/admin/", methods=["GET"])
@login_required
def admin():
    return render_template("admin.html")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

    if exception and db_session.is_active:
        db_session.rollback()


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
        return render_template("sign_up.html", form=form), 404


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


@app.get("/game_menus/")
@redirect_to_game
def game_menu_get():
    game_lobbies = LobbySession.all_lobbies()
    return render_template("menu.html", **{"lobbies": list(game_lobbies)})


@app.post("/game_menus/")
@login_required
def game_menu_post():
    user: User = User.get(session["_user_id"])
    form = LobbySessionForm()
    if form.validate_on_submit():
        data, lobby_index = form.data, LobbySession.get_unique_index()
        name, player_count = data["name"], data["player_count"]
        LobbySession(lobby_index=lobby_index, owner=user, name=name, player_count=player_count)
        return redirect(f"/game_lobby/{lobby_index}/")
    return json.dumps({"errors": form.errors})


@app.route('/game_lobby/<int:lobby_id>/', methods=["GET", "POST"])
@login_required
def lobby(lobby_id: int):
    lobby_session = LobbySession(lobby_index=lobby_id)
    user: User = User.get(session["_user_id"])
    request.user = user
    if request.method == "GET":
        lobby_session.add_user(user)
        return render_template("lobby.html", lobby=lobby_session, game=None)
    elif request.method == "POST":
        if not lobby_session.game_status:
            try:
                GameSession(lobby=lobby_session)
            except ValueError as error:
                logging.info(error)
            else:
                lobby_session.game_status = True
        return redirect(f"/game/{lobby_id}/")


def get_card_template_vars(my_player: Player, cur_player, pair: Pair) -> Dict:
    is_active = "active-player-card" if my_player == cur_player else None
    if pair.attacker == my_player:
        role = "attacker-card"
    elif pair.defender == my_player:
        role = "defender-card"
    else:
        role = None
    return {"active": is_active, "role": role}


def configure_players(g: GameSession, user) -> Tuple[Player, Dict]:
    current_player, finish = g.pair.get_current_player()
    requested_player: Player = g.get_player_by_user(user)

    deck_buffer, table_buffer = g.get_buffer(requested_player)
    for i_player in g.players:
        if deck_buffer or table_buffer:
            i_player.current_cards: List = i_player.cards.current_values()
        else:
            i_player.current_cards: List = list(i_player.cards)
        i_player.vars = get_card_template_vars(i_player, current_player, g.pair)

    context: Dict = {
        "game": g,
        "table": g.pair.table,
        "table_buffer": table_buffer,
        "deck_buffer": deck_buffer
    }
    request.player = requested_player
    return requested_player, context


def set_up_timer(game_ses: GameSession, player: Union[Defender, Attacker]):
    await_before_move: int = 30
    timer = Timer.get_timer_by_player(player, game_ses, await_before_move)
    if timer.time is None:
        return await_before_move
    return await_before_move - (int(time()) - timer.time)


def update_timer(player: Player, *args):
    timer = Timer.get_timer_by_player(player, *args)
    timer.time, timer.process = timer.set_process(*args)


@app.route('/game/<int:game_id>/', methods=["GET", "POST"])
@login_required
def game(game_id: int):
    game_ses: GameSession = GameSession.get_game(game_id)
    is_ajax = request.headers.get('X-Requested-With')
    user: User = User.get(int(session.get("_user_id")))
    lobby_session: LobbySession = LobbySession(lobby_index=game_id)
    if game_ses:
        if game_ses.get_player_by_user(user) in game_ses.players:

            if not session.get("_game_id"):
                session["_game_id"] = game_id
            if is_ajax and request.method == "GET":
                return json.dumps({"message": "Welcome!"}), 200

            requested_player, context = configure_players(game_ses, user)
            current_player, _ = game_ses.pair.get_current_player()
            if request.method == "GET":

                context.update({"lobby": lobby_session})
                return render_template("lobby.html", **context)
            elif request.method == "POST":

                is_updated = requested_player.has_updated_game
                data = {}
                # if requested_player == current_player:
                #     seconds_left = set_up_timer(game_ses, current_player)
                #     data["time"] = seconds_left
                if not is_updated:
                    return render_template("game.html", **context), 202
                return json.dumps(data), 203
            else:
                message, status_code = "Method is not allowed", 400
        else:
            message, status_code = "You're not a part of this game!", 403
    else:
        message, status_code = "Game not found!", 404
    if is_ajax:
        return json.dumps(
            {
                "message": message,
                "url": f"/game_lobby/{game_id}/",
                "user_data": render_template("lobby-users.html", users=lobby_session.users)
            }
        ), status_code
    return redirect(f"/game_lobby/{game_id}/")


def return_action_output(func):
    def wrapper(game_id: int):
        game_ses: GameSession = GameSession.get_game(game_id)
        user: User = User.get(int(session.get("_user_id")))
        if game_ses:
            message, status_code = func(game_id)
        else:
            message, status_code = "Game not found!", 404

        requested_player, context = configure_players(game_ses, user)
        is_updated = requested_player.has_updated_game

        context.update({"message": message})
        if not is_updated:
            return render_template("game.html", **context), status_code
        return json.dumps({"message": message}), status_code
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/game/<int:game_id>/make_move', methods=["POST"])
@return_action_output
@login_required
def make_move_action(game_id: int):
    game_ses: GameSession = GameSession.get_game(game_id)
    user: User = User.get(int(session.get("_user_id")))

    requested_player = game_ses.get_player_by_user(user)
    current_player, _ = game_ses.pair.get_current_player()

    data = request.form.to_dict()

    if requested_player == current_player:
        card_value: str = data.get("card_value")
        table_id: str = data.get("table_id")

        success = current_player.go_on(card_value, game_ses.pair.table, int(table_id))
        if success:
            game_ses.modified()
            return "Ok", 200
            # update_timer(current_player, game_ses, 30)
        requested_player.has_updated_game = False
        return "Your card is lower than attacker's card or you tried to cheat", 202
    return "That is not your turn", 400


@app.route('/game/<int:game_id>/change_status', methods=["POST"])
@return_action_output
@login_required
def change_status_action(game_id: int):
    game_ses: GameSession = GameSession.get_game(game_id)
    user: User = User.get(int(session.get("_user_id")))

    current_player, _ = game_ses.pair.get_current_player()
    requested_player = game_ses.get_player_by_user(user)

    if requested_player == current_player:
        current_player.is_awaken = False
        game_ses.modified()
        return "Updated status", 202
        # update_timer(current_player, game_ses, 30)
    return "Has not updated it", 302


@app.route("/remove_myself/<int:game_id>", methods=["GET"])
@login_required
def remove_player(game_id: int):
    game_ses: GameSession = GameSession.get_game(game_id)
    user: User = User.get(int(session.get("_user_id")))
    if game_ses:
        requested_player: Player = game_ses.get_player_by_user(user)
        if requested_player:
            lobby_ses = LobbySession(lobby_index=game_id)
            game_ses.remove_player(requested_player)
            lobby_ses.users.remove(user)
            game_ses.modified()
            if session.get("_game_id"):
                session.pop("_game_id")
            return redirect("/")
        return redirect("/game_menus/")
    return json.dumps({"message": "Game not found!"}), 404


if __name__ == '__main__':
    Base.metadata.create_all()
    app.run(host="0.0.0.0", port=8000, debug=False)
