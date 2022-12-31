from application.app.game import GameSession, LobbySession, get_users
from application.app.routes import app
import logging


host = "127.0.0.1"
port = 8000


def init_game():
    users = get_users()[:5]
    lobby = LobbySession(lobby_index=1, name="Ultra Game", owner=users[0], people_count=2)
    for user in users:
        lobby.add_user(user)
    g = GameSession(lobby=lobby)
    logging.info(f"Lobby №_{lobby.lobby_index}, Attacker: {g.pair.attacker}, Defender: {g.pair.defender}")


init_game()
if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
