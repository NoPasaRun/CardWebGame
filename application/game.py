import random


class Player:

    def __init__(self, user: dict, player_id):
        self.user = user
        self.player_id = player_id
        self.cards = []


class Game:

    games = []

    def __init__(self, id: int, user: dict):
        if Game.get(id):
            return
        self.id = id
        self.start = False
        self.current_player_pos = 0
        self.coloda = [f"{image}{number}" for image in ["♠", "♣", "♦", "♥"]
                       for number in [6, 7, 8, 9, 10, "V", "D", "K", "T"]]
        player = Player(user, user["id"])
        self.creator = user
        self.current_player, self.bit_player, self.next_player = (None, None, None)
        self.players = [player,]
        Game.games.append(self)

    @classmethod
    def exist(cls, game_id):
        return game_id in [obj.id for obj in cls.games]

    @classmethod
    def get(cls, game_id):
        obj = [game_obj for game_obj in cls.games if game_obj.id == game_id]
        if obj:
            obj, *_ = obj
            return obj
        return None

    def add_player(self, user: dict):
        player = Player(user, user["id"])
        self.players.append(player)

    def update_player_cards(self, player_id: int, cards: list):
        update_player, *_ = [player for player in self.players
                             if player.player_id == player_id]
        [update_player.remove(card) for card in cards]
        new_cards = self.coloda[:len(update_player.cards)]
        update_player.cards.extend(new_cards)
        [self.coloda.remove(card) for card in new_cards]

    def initialize_game(self):
        random.shuffle(self.coloda)
        for i, i_player in zip(range(0, len(self.players)*6, 6), self.players):
            cards_have_used = self.coloda[i:i+6]
            i_player.cards = cards_have_used
        self.current_player_pos = 0

    def initialize_move(self):
        if self.start:
            self.current_player = self.players[self.current_player_pos % len(self.players)]
            self.current_player_pos += 1

