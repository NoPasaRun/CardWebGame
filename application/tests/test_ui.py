from application.app.game import GameSession, LobbySession, get_users
from application.app.routes import app


host = "127.0.0.1"
port = 8000


def init_game():
    lobby = LobbySession(lobby_index=1)
    for user in get_users():
        lobby.add_user(user)
    GameSession(lobby=lobby)


init_game()
