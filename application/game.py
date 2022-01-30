import random


class Player:

    def __init__(self, user: dict, player_id):
        self.user = user
        self.player_id = player_id
        self.active = False
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
        self.table_cards = {}
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

    def delete_player(self, i_player):
        self.players.remove(i_player)
        del i_player

    def add_player(self, user: dict):
        player = Player(user, user["id"])
        self.players.append(player)

    def fill_table(self, i_player, place_id, value_of_card):
        if self.table_cards.get(place_id, False):
            if len(self.table_cards[place_id]) < 2:
                self.table_cards[place_id].append(value_of_card)
                i_player.cards.remove(value_of_card)
        else:
            self.table_cards[place_id] = [value_of_card,]
            i_player.cards.remove(value_of_card)

    def initialize_game(self):
        random.shuffle(self.coloda)
        for i, i_player in zip(range(0, len(self.players)*6, 6), self.players):
            cards_have_used = self.coloda[i:i+6]
            i_player.cards = cards_have_used
        self.current_player_pos = 0
