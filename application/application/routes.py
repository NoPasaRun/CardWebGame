from flask import Flask, request, redirect, session  # import necessary flask modules for web
from flask import render_template  # import modules for sending static files to client
from werkzeug.security import check_password_hash  # function for password secure
from models import create_db, User, Group  # function and models for db work
from settings import template_folder, static_folder  # base static file folder
from game import Game  # patern describing game view work
from flask_wtf import CSRFProtect  # class for authorization
from forms import SignUpForm  # form for sign_up view
from flask_login import LoginManager, login_user, login_required, logout_user  # model and function for login work
from login_view import LoginUser  # creates model based on User class
import os

"""
    Configuring app, 
    creating secret key
"""

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
csrf = CSRFProtect(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
"""
    Editing jinja functions
"""

app.jinja_env.filters['zip'] = zip

"""
    Creating login manager
    Naming login view
"""
login_manager = LoginManager(app)
login_manager.login_view = 'login'

""" 
    Gets user model from User
"""


@login_manager.user_loader
def load_user(user_id: int):
    return LoginUser().fromDB(user_id)


"""
    Index page router
"""


@app.route("/", methods=["GET"])
def main():
    user = session.get("_user_id", False)
    if user:
        is_authenticated = True
    else:
        is_authenticated = False
    return render_template("index.html", is_auth=is_authenticated)


"""
    Admin page router
"""


@app.route("/admin/", methods=["GET"])
@login_required
def admin():
    user = User.get(session["_user_id"])
    group = Group.get(user.group_id)
    if group.title == "advanced":
        return render_template("admin.html")
    return "You have no rights", 401


"""
    Sign up view
"""


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


"""
    Login view
"""


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


"""
    Logout view
"""


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect("/login/")


"""
    Game view
"""


@app.route('/game/<int:game_id>/', methods=["GET", "POST"])
@login_required
def game(game_id: int):
    # Gets user info from DB
    user = User.get(session["_user_id"])
    user = {"id": user.id, "username": user.username, "age": user.age}
    return_to_post = False
    if request.method == "GET":
        # Check if game is existing
        if Game.exist(game_id):
            game_ses = Game.get(game_id)
            if game_ses.start:
                if user["id"] not in [player.player_id for player in game_ses.players]:
                    # Denying join request if game has started
                    return "Game has already started", 400
            else:
                if user["id"] not in [player.player_id for player in game_ses.players]:
                    if len(game_ses.players) == 6:
                        # Denying join request if game is already having 6 members
                        return "The game is full of people", 400
                    # Adding player to game
                    game_ses.add_player(user)
            i_player = [i_player for i_player in game_ses.players if i_player.player_id == user["id"]]
            if i_player:
                i_player = i_player[0]
                # Sending page to player
                return render_template("game.html", game=game_ses, i_player=i_player)
        else:
            Game(game_id, user)
            # Redirecting player to same page in order update info on page
            return redirect(f"/game/{game_id}/")
    if request.method == "POST" or return_to_post:
        if Game.exist(game_id):
            game_ses = Game.get(game_id)
            i_player = [i_player for i_player in game_ses.players if i_player.player_id == user["id"]]
            if i_player:
                i_player = i_player[0]
                # Starting game
                if request.form.get("start-game", False):
                    if user["id"] == game_ses.creator["id"]:
                        game_ses.start = True
                        game_ses.initialize_game()
                        game_ses.init_move()
                        return redirect(f"/game/{game_id}/")
                    else:
                        return "You have no rights", 300
                # Updating cards in cells on page
                if request.form.get("update-table", False):
                    value_of_card = request.form.get("card")
                    place_id = request.form.get("place_id")
                    game_ses.fill_table(i_player=i_player, place_id=place_id, value_of_card=value_of_card)
                # Initialize the player who gonna move next
                if request.form.get("continue-move", False):
                    game_ses.continue_move()
                # Sending html page for ajax request (page must not be reloaded)
                if request.form.get("update-page", False):
                    return render_template("game-info.html", game=game_ses, i_player=i_player)
            return redirect("/")
        return "The game is ended or has not created yet", 400


if __name__ == '__main__':
    # creating DB if it is not exist
    create_db(create_superuser=True)
    # creating test game
    test = False
    if test:
        game = Game(1, {"id": 1, "username": "NoPasaRan", "age": 16})
        [game.add_player({"id": i, "username": User.get(i).username, "age": User.get(i).age}) for i in range(2, 2)]
    # Initializing app
    csrf.init_app(app)
    # Launching app
    app.run(host="0.0.0.0", port=8000)
