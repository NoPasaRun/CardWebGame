from application.app.game import GameSession, LobbySession, get_users
from application.app.routes import app
import logging


host = "127.0.0.1"
port = 8000


def init_game():
    lobby = LobbySession(lobby_index=1)
    for user in get_users()[:3]:
        lobby.add_user(user)
    g = GameSession(lobby=lobby)
    logging.info(f"Lobby №_{lobby.lobby_index}, Attacker: {g.pair.attacker}, Defender: {g.pair.defender}")


init_game()
if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
