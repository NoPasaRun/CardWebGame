import random
from typing import Iterable


class Player:

    def __init__(self, user: dict, player_id: int):
        self.user = user
        self.player_id = player_id
        self.classname = None
        self.active = False
        self.state = None
        self.cards = []


class Move:

    move = None
    pas = "pas"
    bit = "bit"

    def __init__(self, attack: Player, defend: Player, attack_2: Player):
        self.attacker = attack
        attack.classname = "attack"
        self.defender = defend
        defend.classname = "defend"
        self.attacker_2 = attack_2
        attack_2.classname = "attack"
        self.is_now = True
        self.next_function = None
        Move.move = self

    def get_players(self) -> Iterable[Player]:
        return self.attacker, self.defender, self.attacker_2

    def attack(self) -> str:
        if self.attacker.state != Move.bit:
            self.attacker_2.active = False
            self.defender.active = False
            self.attacker.active = True
            if self.defender.state != Move.pas:
                self.next_function = self.defend
            else:
                self.next_function = self.attack
            return "continue"
        elif self.attacker_2.state != Move.bit:
            self.attack_2()
        return "finish"

    def defend(self) -> str:
        if self.defender.state != self.pas:
            self.attacker_2.active = False
            self.defender.active = True
            self.attacker.active = False
            if self.attacker.state != Move.bit:
                self.next_function = self.attack
            else:
                self.next_function = self.attack_2
            return "continue"
        elif self.attacker.state != Move.bit:
            self.attack()
        elif self.attacker_2.state != Move.bit:
            self.attack_2()
        return "finish"

    def attack_2(self) -> str:
        if self.attacker_2.state != self.bit:
            self.attacker_2.active = True
            self.defender.active = False
            self.attacker.active = False
            if self.defender.state != Move.pas:
                self.next_function = self.defend
            else:
                self.next_function = self.attack_2
            return "continue"
        elif self.attacker.state != Move.bit:
            self.attack()
        return "finish"

    def move_prediction(self) -> str:
        if self.is_now:
            output = self.attack()
            self.is_now = False
        else:
            output = self.next_function()
        return output


class Game:

    games = []

    def __init__(self, id: int, user: dict):
        if Game.get(id):
            return
        self.id = id
        self.start = False
        self.pos = 0
        self.coloda = [f"{image}{number}" for image in ["♠", "♣", "♦", "♥"]
                       for number in [6, 7, 8, 9, 10, "V", "D", "K", "T"]]
        self.kozir = None
        player = Player(user, user["id"])
        self.creator = user
        self.table_cards = {}
        self.players = [player, ]
        Game.games.append(self)

    @classmethod
    def exist(cls, game_id) -> bool:
        return game_id in [obj.id for obj in cls.games]

    @classmethod
    def get(cls, game_id: int):
        obj = [game_obj for game_obj in cls.games if game_obj.id == game_id]
        if obj:
            obj, *_ = obj
            return obj
        return None

    def delete_player(self, i_player: Player) -> None:
        self.players.remove(i_player)
        del i_player

    def add_player(self, user: dict):
        player = Player(user, user["id"])
        self.players.append(player)

    def fill_table(self, i_player: Player, place_id: str, value_of_card: str) -> None:
        if self.table_cards.get(place_id, False):
            if len(self.table_cards[place_id]) < 2:
                self.table_cards[place_id].append(value_of_card)
                i_player.cards.remove(value_of_card)
        else:
            self.table_cards[place_id] = [value_of_card, ]
            i_player.cards.remove(value_of_card)

    def update_cards_for_all(self, players: Iterable[Player]) -> None:
        self.table_cards.clear()
        for player in players:
            for i in range(6-len(player.cards)):
                try:
                    update_card = self.coloda[0]
                    player.cards.append(update_card)
                    self.coloda.remove(update_card)
                except IndexError:
                    pass

    def update_cards_defender_lost(self, attack_player: Player, lost_player: Player, attack_2_player: Player) -> None:
        lost_player.cards.extend(self.table_cards.values())
        self.update_cards_for_all([attack_player, attack_2_player])

    def initialize_game(self) -> None:
        random.shuffle(self.coloda)
        for i, i_player in zip(range(0, len(self.players)*6, 6), self.players):
            cards_have_used = self.coloda[i:i+6]
            i_player.cards = cards_have_used
        self.kozir = self.coloda[-1]

    def init_move(self, move_num: int = 0) -> None:
        for player in self.players:
            if len(player.cards) == 0:
                self.players.remove(player)
        if len(self.players) > 1:
            self.pos += move_num
            if Move.move:
                del Move.move
            players_in_move = [self.players[i % len(self.players)] for i in range(self.pos, self.pos+3)]
            Move(*players_in_move)
            self.continue_move()
        else:
            Game.games.remove(self)
            del self

    def continue_move(self) -> None:
        if Move.move:
            if len([val for val_list in self.table_cards.values()
                    for val in val_list]) < 12:
                move_output = Move.move.move_prediction()
                if move_output == "continue":
                    return
            cur_players = Move.move.get_players()
            if cur_players[1].state == "pas":
                self.update_cards_defender_lost(*Move.move.get_players())
                num = 2
            else:
                self.update_cards_for_all(Move.move.get_players())
                num = 1
            self.init_move(num)
