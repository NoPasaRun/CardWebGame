from application.app.game import GameSession, LobbySession, User
from application.app.routes import app
import logging


host = "192.168.31.52"
port = 8000


def init_game():
    users = [User.get_by_username("NoPasaRan"), User.get_by_username("Stan")]
    lobby = LobbySession(lobby_index=1, name="Ultra Game", owner=users[0], player_count=6)
    for user in users:
        lobby.add_user(user)
    g = GameSession(lobby=lobby)
    logging.info(f"Lobby №_{lobby.lobby_index}, Attacker: {g.pair.attacker}, Defender: {g.pair.defender}")


if __name__ == '__main__':
    init_game()
    app.run(host=host, port=port)