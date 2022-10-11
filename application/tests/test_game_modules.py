import unittest
from application.application.game import GameSession, Card, get_users, OFF
from application.application.game import HEARTS, SPADES, DIAMONDS, CLUBS


class PlayerCardsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        user_data = get_users()[:2]
        assert len(user_data) == 2
        self.game_session = GameSession(user_data=user_data, game_index=1)
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
        replaced_players = self.game_session.replace_player_with_trump(self.game_session.players)
        self.assertEqual(replaced_players[0], self.second_player)

    def tearDown(self) -> None:
        del self.game_session


class PairPlayerActivityTestCase(unittest.TestCase):
    def setUp(self) -> None:
        user_data = get_users()[:3]
        assert len(user_data) == 3
        self.game_session = GameSession(user_data=user_data, game_index=1)
        self.pair = self.game_session.pair
        self.first_player = self.game_session.players[0]
        self.second_player = self.game_session.players[1]
        self.third_player = self.game_session.players[2]

    def test_change_attacker(self):
        self.pair.change_attacker(self.pair.defender)
        self.assertNotEqual(self.pair.defender.user_data, self.pair.attacker.user_data)

    def tearDown(self) -> None:
        del self.game_session


class GameplayScenarioTestCase(unittest.TestCase):
    def setUp(self) -> None:
        user_data = get_users()[:3]
        assert len(user_data) == 3
        self.game_session = GameSession(user_data=user_data, game_index=1)
        self.pair = self.game_session.pair

    def test_finishing_pair(self):
        self.pair.attacker.is_awaken = False
        self.pair.get_current_player()
        self.assertNotEqual(self.pair, self.game_session.pair)

    def test_defender_pass_attacker_move(self):
        self.pair.table[1][OFF] = self.pair.attacker.cards[0]
        self.pair.defender.is_awaken = False
        current_player = self.pair.get_current_player()
        self.assertEqual(current_player, self.pair.attacker)

    def test_change_attacker_if_attacker_has_passed(self):
        new_attacker = None
        for i_player in self.game_session.players:
            if i_player not in self.pair.pair_players:
                new_attacker = i_player
        self.pair.attacker.is_awaken = False
        self.pair.change_attacker(new_attacker)
        self.assertEqual(new_attacker, self.pair.attacker)

    def test_change_attacker_is_not_allowed(self):
        new_attacker = None
        for i_player in self.game_session.players:
            if i_player not in self.pair.pair_players:
                new_attacker = i_player
        self.pair.change_attacker(new_attacker)
        self.assertNotEqual(new_attacker, self.pair.attacker)

    def tearDown(self) -> None:
        del self.game_session
