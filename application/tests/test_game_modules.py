import unittest
from application.application.game import GameSession, Card, Pair, get_users
from application.application.game import HEARTS, SPADES, DIAMONDS, CLUBS


class PlayerCardsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        user_data = get_users()[:2]
        assert len(user_data) == 2
        self.game_session = GameSession(user_data=user_data)
        self.game_session.trump = Card(12, HEARTS, False)
        self.trump = self.game_session.trump
        self.first_player = self.game_session.players[0]
        self.second_player = self.game_session.players[1]

    def test_player_with_min_trump_is_first(self):
        self.first_player.cards = [
            Card(num, suit, self.trump)
            for num, suit in [(7, CLUBS), (11, HEARTS), (6, SPADES)]
        ]
        self.second_player.cards = [
            Card(num, suit, self.trump)
            for num, suit in [(10, HEARTS), (12, DIAMONDS), (8, CLUBS)]
        ]
        replaced_players = self.game_session.replace_player_with_trump([self.first_player, self.second_player])
        self.assertEqual(replaced_players[0], self.second_player)

    def tearDown(self) -> None:
        del self.game_session


class PairPlayerActivityTestCase(unittest.TestCase):
    def setUp(self) -> None:
        user_data = get_users()[:3]
        assert len(user_data) == 3
        self.game_session = GameSession(user_data=user_data)
        self.pair = Pair(self.game_session)
        self.first_player = self.game_session.players[0]
        self.second_player = self.game_session.players[1]
        self.third_player = self.game_session.players[2]

    def test_change_attacker(self):
        self.pair.change_attacker(self.pair.defender)
        self.assertNotEqual(self.pair.defender.user_data, self.pair.attacker.user_data)

    def tearDown(self) -> None:
        del self.game_session


class PairGameSessionSharingDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        user_data = get_users()
        self.first_game_session = GameSession(user_data=user_data)
        self.second_game_session = GameSession(user_data=user_data)
        self.pair = Pair(self.second_game_session)

    def test_pair_no_rights_to_change_game_data(self):
        players_data_before_end = self.first_game_session.players
        self.pair.table = {key: value for key, value in [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]}
        self.pair.get_current_player(self.first_game_session)
        self.assertEqual(self.first_game_session.players, players_data_before_end)

    def test_pair_rights_to_change_game_data(self):
        players_data_before_end = self.second_game_session.players
        self.pair.table = {key: value for key, value in [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]}
        self.pair.get_current_player(self.second_game_session)
        self.assertNotEqual(self.second_game_session.players, players_data_before_end)

    def tearDown(self) -> None:
        del self.first_game_session, self.second_game_session
