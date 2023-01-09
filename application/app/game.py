import random
from typing import Dict, List, Tuple, Union, Callable, Iterable
import logging
from application.app.models import User


def get_users() -> List[User]:
    """
    Функция возвращающая информацию о пользователях
    :return:
    Список данных пользователя или объекты модели User
    """
    data = User.all()
    return data


CARDS_IN_DECK: int = 36
DEF = "defender_card"
OFF = "offensive_card"

HEARTS, DIAMONDS, SPADES, CLUBS = SIGNS = ("❤", "♦", "♠", "♣")
DECK: List[Tuple] = [(number, suit) for suit in SIGNS for number in range(6, 15)]
EXTRA_NUMBERS: Dict = {11: "V", 12: "D", 13: "K", 14: "T"}

PLAYER_LOW_AMOUNT, PLAYER_HIGH_AMOUNT = 2, 6
CARDS_FOR_PLAYER: int = 6


class Deck(list):

    def __getitem__(self, index) -> Union['Deck', 'Card']:
        output = super().__getitem__(index)
        values = [output] if not isinstance(output, list) else output
        for val in values:
            self.remove(val)
        return output if not isinstance(output, list) else Deck(output)

    def shuffle(self):
        shuffled_deck = self.copy()
        random_indexes = list(range(len(self)))

        random.shuffle(random_indexes)
        for index, random_index in enumerate(random_indexes):
            self[index] = shuffled_deck[random_index]

    def get_card_by_string(self, value: str) -> 'Card':
        list_of_string_cards = [str(card) for card in self]
        if value in list_of_string_cards:
            index = list_of_string_cards.index(value)
            return super().__getitem__(index)


class PlayerDeck(Deck):

    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.__clear_buffer = True
        self.__buffer = []
        self.__table_buffer = {}

    @property
    def clear_buffer(self):
        value = self.__clear_buffer
        self.__clear_buffer = False
        return value

    @clear_buffer.setter
    def clear_buffer(self, value):
        return

    def current_values(self):
        deck, additional_cards = self.copy(), self.__buffer + self.table_values
        cards = set(deck).difference(additional_cards)
        return cards

    @property
    def table_buffer(self):
        value = self.__table_buffer.copy()
        return value

    @property
    def table_values(self) -> List:
        for player, table_cards in self.table_buffer.items():
            return table_cards
        return []

    @table_buffer.setter
    def table_buffer(self, value: Dict):
        self.__table_buffer = value
        self.__clear_buffer = True

    @property
    def buffer(self):
        buf = self.__buffer.copy()
        return buf

    @buffer.setter
    def buffer(self, value):
        return

    def extend(self, iterable, update_buffer: bool = True):
        super().extend(iterable)
        self.__clear_buffer = True
        self.__buffer = iterable if update_buffer else []

    def append(self, obj, update_buffer: bool = True):
        super().append(obj)
        self.__clear_buffer = True
        self.__buffer = obj if update_buffer else []


class Card:
    """
    Класс, описывающий поведение Карт
    """

    def __init__(self, number: int, sign: str, is_not_trump: Union['Card', bool]) -> None:
        """
        Функция конструктор

        :param number: номинал карты
        :param sign: масть карты
        :param is_not_trump: логическое "не козырная карта" или Карта, являющаяся козырем
        """
        self.val: int = number
        self.suit: str = sign
        self.color: str = "red" if sign in (HEARTS, DIAMONDS) else "black"
        if is_not_trump:
            # если карта не выбрана козырем, но масть совпадает с мастью козыря, то карта - козырь
            self.is_trump = sign == is_not_trump.suit
        else:
            # если карта козырь, то "не козырная карта" меняется на "козырная карта
            self.is_trump = not is_not_trump

    def __repr__(self) -> str:
        """
        Строковое представление Карт
        :return:
        Строка вида "номинал + масть"
        """
        number: str = str(EXTRA_NUMBERS.get(self.val, self.val))
        return number + self.suit

    def __gt__(self, c: 'Card') -> bool:
        """
        Сравнение Карт
        :param c: Карта
        :return:
        Карта больше или меньше переданной
        """
        # Козырь всегда больше не козырной карты
        if self.is_trump and not c.is_trump:
            return True
        else:
            # Если козыри совпадают, то сравниваются номиналы
            if self.suit == c.suit:
                return self.val > c.val
            return False

    @classmethod
    def min_trump_card(cls, cards: List['Card']) -> ['Card', bool]:
        """
        Функция, находящая козырную Карту с наименьшим номиналом в списке
        :param cards: Список Карт
        :return:
        Минимальный козырь (если есть) или логическое "нет козыря"
        """
        card_with_min_val, first_card = cards[0], cards[0]
        # цикл нахождения минимального козыря
        for card in cards:
            if card < card_with_min_val and card.is_trump or not card_with_min_val.is_trump:
                card_with_min_val = card
        # если первая выбранная карта для сравнения не козырь, то козыря нет
        if first_card == card_with_min_val and not first_card.is_trump:
            return False
        return card_with_min_val

    @staticmethod
    def remove_cards_from_dec(deck: List['Card'], cards: List['Card']) -> List['Card']:
        deck, cards = set(deck), set(cards)
        deck.difference_update(cards)
        return list(deck)


def check_if_players_are_out(func: Callable):
    def wrapper(self: 'GameSession', *args, **kwargs):
        result = func(self, *args, **kwargs)
        if len(self.cards) == 0:
            for i_player in self.players:
                if len(i_player.cards) == 0:
                    self.remove_player(i_player)
        return result
    return wrapper


class Player:
    """
    Класс, описывающий атрибуты Игрока
    """

    def __init__(self, user_data: User, cards: PlayerDeck[Card], has_updated_game: bool = True) -> None:
        """
        Функция конструктор
        :param user_data: данные пользователя / объект модели User
        :param cards: Карты Игрока
        """
        self.user_data: User = user_data
        self.cards: PlayerDeck = cards
        self.__has_updated_game = has_updated_game
        parameters = list(self.__dict__.keys())
        self.parameters = parameters

    def __setattr__(self, key, value):
        if key == "cards":
            if isinstance(value, PlayerDeck):
                super().__setattr__(key, value)
            else:
                super().__setattr__(key, PlayerDeck())
                if isinstance(value, Iterable):
                    self.cards.extend(value)
                else:
                    self.cards.append(value)
        else:
            super().__setattr__(key, value)

    def __hash__(self) -> int:
        pl = Player(*self.__getargs__())
        delattr(pl, "cards")
        return super(Player, pl).__hash__()

    @property
    def has_updated_game(self):
        value = self.__has_updated_game
        self.__has_updated_game = True
        return value

    @has_updated_game.setter
    def has_updated_game(self, value):
        self.__has_updated_game = value

    def go_on(self, card_val: str, table: 'Table', table_id: int) -> bool:
        """
        Функция подкидывания Карты
        :param card_val: строковое представление Карты
        :param table: Стол
        :param table_id: ячейка Стола
        :return:
        Логическое подкинул: да/нет
        """
        # если переданная Карта есть в списке Карт Игрока, то удаляем ее из списка
        table_card: Card = self.cards.get_card_by_string(card_val)
        if table_card:
            # если Карту можно поставить на Стол, то удаляем ее из списка
            if table.put_card(table_id, table_card):
                self.cards.remove(table_card)
                return True
        return False

    def __eq__(self, other: Union['Player', 'Attacker', 'Defender']) -> bool:
        if other is not None:
            return self.user_data == other.user_data
        return False

    def __getargs__(self) -> Tuple:
        """
        Функция, возвращающая атрибуты класса
        :return:
        Кортеж атрибутов
        """
        parameters: Tuple = tuple([getattr(self, attr) for attr in self.parameters])
        return parameters

    def to_player(self):
        return Player(*self.__getargs__())

    def __repr__(self):
        return self.user_data.__repr__()


class Attacker(Player):
    """
    Класс, описывающий поведения Игрока-Подкидывающего
    """

    def __init__(self, pl: Player) -> None:
        """
        Функция конструктор
        :param pl:
        """
        args: Tuple = pl.__getargs__()
        super().__init__(*args)
        # атрибут, показывающий логическое "бито"
        self.__is_awaken: bool = True

    @property
    def is_awaken(self) -> bool:
        return self.__is_awaken

    @is_awaken.setter
    def is_awaken(self, value: bool):
        self.__is_awaken = value


class Defender(Player):
    """
    Класс, описывающий поведение Игрока-Покрывающего
    """

    def __init__(self, pl: Player) -> None:
        """
        Функция конструктор
        :param pl:
        """
        args: Tuple = pl.__getargs__()
        super().__init__(*args)
        # атрибут, показывающий логическое "пас"
        self.__is_awaken = True

    @property
    def is_awaken(self) -> bool:
        return self.__is_awaken

    @is_awaken.setter
    def is_awaken(self, value: bool):
        self.__is_awaken = value


class GameSession:
    """
    Класс описывающий методы и атрибуты Игровой Сессии
    """
    __games: Dict = {}

    def __init__(self, lobby: 'LobbySession') -> None:
        """
        Функция конструктор
        """
        try:
            self._id = lobby.lobby_index
            self.__cards, self.trump = self.make_deck()
            self.__players: List = self.shuffle_players(lobby.users[:lobby.player_count])
            self.__pair = Pair(self)
            GameSession.__games[self._id] = self
        except AssertionError as error:
            raise ValueError(error)

    @classmethod
    def game_exists(cls, game_ses) -> bool:
        return game_ses in cls.__games.values()

    @classmethod
    def all_games(cls):
        return cls.__games

    def delete(self):
        if GameSession.game_exists(self):
            lobby_session = LobbySession(lobby_index=self._id)
            GameSession.__games.pop(self._id)
            lobby_session.game_status = False

    @check_if_players_are_out
    def modified(self):
        if hasattr(self, "players"):
            for i_player in self.players:
                i_player.has_updated_game = False

    def get_buffer(self, requested_player: Player) -> [Dict, Dict]:
        if requested_player is not None:
            if requested_player.cards.clear_buffer:
                deck_buffer, table_buffer = {}, requested_player.cards.table_buffer
                for i_player in sorted(self.players, key=lambda pl: self.trump in pl.cards):
                    buffer_cards = i_player.cards.buffer
                    cards = list([
                        (card if i_player == requested_player or card == self.trump else None)
                        for card in sorted(buffer_cards, key=lambda c: c == self.trump)]
                    )
                    deck_buffer.update({i_player: cards})
                return deck_buffer, table_buffer
        return {}, {}

    def iter_players(self, requested_player: Player) -> List:
        req_player_index = self.players.index(requested_player)
        main_player_list = self.players[req_player_index+1:] + self.players[:req_player_index+1]
        return main_player_list

    @property
    def pair(self):
        return self.__pair

    @pair.setter
    def pair(self, val):
        return

    @classmethod
    def get_game(cls, index: int):
        return cls.__games.get(index)

    @property
    def players(self) -> List[Player]:
        return self.__players

    @property
    def cards(self) -> Deck[Card]:
        return self.__cards

    @players.setter
    def players(self, new_list_of_players: List[Player]) -> None:
        self.__players: List = new_list_of_players

    @cards.setter
    def cards(self, used_cards) -> None:
        set_of_cards = set(self.__cards)
        set_of_cards.difference_update(used_cards)
        self.__cards = list(set_of_cards)

    def remove_player(self, pl: 'Player'):
        self.players.remove(pl)
        if len(self.players) <= 1:
            self.delete()

    def get_player_by_user(self, user: User) -> Player:
        for i_player in self.players:
            if i_player.user_data == user:
                return i_player

    @staticmethod
    def make_deck() -> Tuple[Deck[Card], Card]:
        """
        Функция создания колоды Карт
        :return:
        Колода Карт и козырная Карта
        """

        deck: List = DECK.copy()
        # берем рандомные значения из списка - это данные козыря
        random_card_value: Tuple[int, str] = random.choice(deck)

        # конвертируем данные карт в объекты Карт
        trump, _ = Card(*random_card_value, is_not_trump=False), deck.remove(random_card_value)
        deck: Deck = Deck([Card(*card_value, is_not_trump=trump) for card_value in deck]+[trump])
        # мешаем колоду
        deck.shuffle()

        assert len(deck) == CARDS_IN_DECK
        return deck, trump

    def clear_deck(self):
        self.__cards = Deck()

    @staticmethod
    def replace_player_with_trump(shuffled_players: List[Player]) -> List[Player]:
        """
        Функция, ставящая Игрока с минимальной козырной Картой в начало списка
        :param shuffled_players: Игроки
        :return:
        Отсортированный список
        """
        using_cards = []
        # Создаем список всех карт Игроков
        for shuffled_player in shuffled_players:
            using_cards.extend(shuffled_player.cards)

        # Получаем минимальный козырь и ищем Игрока, у которого он есть
        min_card = Card.min_trump_card(using_cards)
        for shuffled_player in shuffled_players:
            if min_card in shuffled_player.cards:
                shuffled_players.remove(shuffled_player)
                shuffled_players.insert(0, shuffled_player)
                break
        return shuffled_players

    def set_pair(self):
        self.__pair = Pair(self)

    def shuffle_players(self, users: Union[List[User]]) -> List[Player]:
        """
        Функция создания Игроков и раздачи Карт
        :param users: данные Игроков
        :return:
        Список Игроков
        """
        cards_for_player: List = []
        # Сортировка Карт
        for i in range(len(users)):
            player_cards = self.cards[:CARDS_FOR_PLAYER]
            cards_for_player.append(player_cards)

        # Конвертируем данные Игрока в объекты Игроков
        players: List = [
            Player(user, players_cards)
            for user, players_cards in zip(users, cards_for_player)
        ]
        # Ставим Игрока с минимальным козырем в начало списка
        players: List = self.replace_player_with_trump(players)

        assert PLAYER_LOW_AMOUNT <= len(players) <= PLAYER_HIGH_AMOUNT
        return players


class LobbySession:

    __lobbies: Dict = {}
    lobby_count_range = [0, 8_000_000_000]

    def __init__(self, lobby_index: int, **kwargs):
        if LobbySession.get_lobby(lobby_index) is None:
            self.__users = []
            self.__ready_to_play = False
            self.__lobby_index = lobby_index
            self.owner = kwargs.get("owner", User())
            if self.owner.id is not None:
                self.add_user(self.owner)
            self.name = kwargs.get("name", "")
            self.player_count = kwargs.get("player_count", 6)
            LobbySession.__lobbies[lobby_index] = self

    def __new__(cls, lobby_index, **kwargs):
        if LobbySession.get_lobby(lobby_index) is not None:
            return LobbySession.get_lobby(lobby_index)
        return super(LobbySession, cls).__new__(cls)

    @classmethod
    def get_unique_index(cls) -> int:
        list_of_numbers = [lobby.lobby_index for lobby in cls.all_lobbies()] + cls.lobby_count_range
        list_of_indexes = sorted(set(list_of_numbers))
        pair_numbers = map(lambda pair: (list_of_indexes[pair[0] + 1], pair[1]), enumerate(list_of_indexes[:-1]))
        for bigger_num, smaller_num in pair_numbers:
            if bigger_num - smaller_num > 1:
                return smaller_num + 1

    @classmethod
    def all_lobbies(cls) -> Iterable['LobbySession']:
        return cls.__lobbies.values()

    @property
    def users(self):
        return self.__users

    @classmethod
    def get_lobby(cls, lobby_index: int) -> 'LobbySession':
        lobby = cls.__lobbies.get(lobby_index, None)
        return lobby

    @property
    def lobby_index(self):
        return self.__lobby_index

    @lobby_index.setter
    def lobby_index(self, val):
        return

    @property
    def game_status(self):
        return self.__ready_to_play

    @game_status.setter
    def game_status(self, status_bool):
        self.__ready_to_play = status_bool

    def add_user(self, user: User):
        if user not in self.users:
            self.users.append(user)


def check_if_game_is_valid(func: Callable):
    def wrapper(self, *args, **kwargs):
        if GameSession.game_exists(self.game_ses):
            return func(self, *args, **kwargs)
    return wrapper


def pair_tracker(decorator: Callable):
    def wrapper(cls):
        for str_method in dir(cls):
            method = getattr(cls, str_method)
            if not (str_method.startswith("__") or isinstance(method, property)):
                new_method = decorator(method)
                setattr(cls, str_method, new_method)
        return cls
    return wrapper


@pair_tracker(check_if_game_is_valid)
class Pair:
    """
    Класс описывающий Пару Игроков (Подкидывающий/Покрывающий)
    """

    def __init__(self, game_ses: GameSession) -> None:
        """
        Функция конструктор
        :param game_ses: объект Игровой Сессии
        """
        self.table: Table = Table()

        # Два первых Игрока в списке - Подкидывающий/Покрывающий
        pair_players: List[Player] = game_ses.players[:2]
        player_classifier = zip((Attacker, Defender), pair_players)

        self.attacker, self.defender = [obj_class(pair_player) for obj_class, pair_player in player_classifier]
        for index, i_player in enumerate([self.attacker, self.defender]):
            game_ses.players[index] = i_player
        self.__game_ses = game_ses

    @property
    def game_ses(self):
        return self.__game_ses

    @game_ses.setter
    def game_ses(self, value):
        return

    @property
    def pair_players(self) -> List[Player]:
        pair_players = [self.attacker]
        if not self.defender.is_awaken:
            pair_players.append(self.defender)
        return pair_players

    @pair_players.setter
    def pair_players(self, value: List[Player]):
        return

    def do_someone_go_on(self, attacker_move: bool) -> Union[Union[Attacker, Defender], bool]:
        """
        Функция, определяющая, кто ходит (или никто не ходит вообще)
        :param attacker_move: логическое "следующим ходит Подкидывающий"
        :return:
        Игрок, который ходит, или логическое "никто не ходит"
        """
        off_cells, def_cells = [self.table.free_cells(key) for key in [OFF, DEF]]
        if (attacker_move or not self.defender.is_awaken) and self.attacker.is_awaken and off_cells > 0:
            # Если до этого сходил Покрывающий, а Подкидывающий активен (не бито), то он ходит | макс 6 Карт
            active_player: Attacker = self.attacker
        elif not attacker_move and self.defender.is_awaken and def_cells > 0:
            # Если до этого сходил Подкидывающий, а Покрывающий активен (не пас), то он ходит | макс 6 Карт
            active_player: Defender = self.defender
        else:
            # Иначе никто не ходит
            return False
        return active_player

    def get_current_player(self) -> Union[Attacker, Defender]:
        """
        Функция, возвращающая активного игрока завершающая Игровую Пару
        :return:
        Игрок или Игровая Сессия с измененными параметрами (атрибутами)
        """
        attacker_next_move = self.table.is_last_defender_card()
        # Получаем текущего пользователя
        current_player: Union[Union[Attacker, Defender], bool] = self.do_someone_go_on(attacker_next_move)
        if current_player:
            return current_player
        # Заканчиваем Игровую Пару
        return self.finish_pair()

    def change_attacker(self, thrower: Player) -> None:
        """
        Функция смены Подкидывающего
        :param thrower: Игрок
        :return:
        """
        # Если у текущего Подкидывающего бито, то новый Подкидывающий - переданный Игрок
        thrower_index = self.game_ses.players.index(thrower)
        if not self.attacker.is_awaken and thrower != self.defender:
            self.attacker = self.game_ses.players[thrower_index] = Attacker(thrower)

    def leave_loser(self) -> None:
        """
        Функция, удаляющая Покрывающего Игрока, если тот все покрыл
        :return:
        """
        # Если у Покрывающего Игрока не пас, то при новой Паре, он будет Подкидывающим
        table_cards = self.table.cards
        if not self.defender.is_awaken:
            self.table.table_buffer[self.defender] = table_cards
            self.defender.cards.extend(table_cards, False)
        else:
            self.table.table_buffer = {}

    def give_cards_to_players(self) -> None:
        """
        Функция, раздающая недостающие Карты Игрокам
        :game_ses: Игровая Сессия
        :return:
        """
        for i_player in self.game_ses.players:
            cards_to_add: int = CARDS_FOR_PLAYER - len(i_player.cards)
            if cards_to_add > 0:
                cards_to_add: Deck[Card] = self.game_ses.cards[:cards_to_add]
                i_player.cards.extend(cards_to_add)
            else:
                i_player.cards.extend([], False)
            i_player.cards.table_buffer = self.table.table_buffer.copy()

    def replace_players(self) -> None:
        """
        Функция, меняющая порядок Игроков
        :game_ses: Игровая Сессия
        :return:
        """
        # Первые два (или один - в зависимости от исхода Пары) игрока отправляются в конец списка
        for i_player in self.pair_players:
            self.game_ses.players.remove(i_player)
            self.game_ses.players.append(i_player.to_player())

    def finish_pair(self) -> Attacker:
        """
        Функция, закрывающая Пару и обновляющая данные Игровой Сессии
        :return:
        Игровая Сессия
        """
        # Перед сменой мест Игроков в списке, важно определить нового Подкидывающего
        self.leave_loser()
        self.give_cards_to_players()
        self.replace_players()
        self.game_ses.set_pair()
        return self.game_ses.pair.attacker


class Table(dict):
    def __init__(self):
        self.table_buffer = {}
        table_data = {key: {OFF: None, DEF: None} for key in range(1, 7)}
        super().__init__(table_data)

    def is_last_defender_card(self) -> bool:
        values = [(data_cell[OFF], data_cell[DEF]) for data_cell in self.values()]
        for off_card, def_card in values:
            if off_card and not def_card:
                return False
        return True

    def put_card(self, table_id: int, card: Card):
        if table_id in self.keys():
            off_card, def_card = self[table_id].values()
            if off_card is None:
                if card.val in [c.val for c in self.cards] or self.cards == []:
                    self[table_id][OFF] = card
                    return True
            elif def_card is None:
                if card > off_card:
                    self[table_id][DEF] = card
                    return True

    def get_items(self) -> List[Tuple[int, Tuple]]:
        items = [(index, (data_cell[OFF], data_cell[DEF])) for index, data_cell in self.items()]
        return items

    @property
    def cards(self) -> List[Card]:
        cards = [card for data_cell in self.values() for card in data_cell.values() if card is not None]
        return cards

    def free_cells(self, key: str) -> int:
        free_cells = [
            c for data_cell in self.values()
            for cell_key, c in data_cell.items()
            if c is None and cell_key == key
        ]
        return len(free_cells)


if __name__ == '__main__':
    pass
