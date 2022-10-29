import random
from typing import Dict, List, Tuple, Union, Callable

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


class GameSessionAddon:
    def __init__(self, game_ses: 'GameSession'):
        self.__game_ses = game_ses

    @property
    def game_ses(self):
        return self.__game_ses

    @game_ses.setter
    def game_ses(self, value):
        return

    def __setattr__(self, key, value):
        super(GameSessionAddon, self).__setattr__(key, value)
        if hasattr(self, "game_ses"):
            self.game_ses.modified()


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

    def __gt__(self, card: 'Card') -> bool:
        """
        Сравнение Карт
        :param card: Карта
        :return:
        Карта больше или меньше переданной
        """
        # Козырь всегда больше не козырной карты
        if self.is_trump and not card.is_trump:
            return True
        else:
            # Если козыри совпадают, то сравниваются номиналы
            if self.suit == card.suit:
                return self.val > card.val
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


def check_if_player_is_out(func: Callable):
    def wrapper(self: Union['Defender', 'Player', 'Attacker'], game_ses: 'GameSession', *args, **kwargs):
        result = func(self, game_ses, *args, **kwargs)
        if len(self.cards) == 0 and (isinstance(self, Defender) or len(game_ses.cards) == 0):
            if len(game_ses.cards) == 0:
                game_ses.remove_player(self)
            if isinstance(self, Defender):
                game_ses.pair.finish_pair()
        return result
    return wrapper


class Player:
    """
    Класс, описывающий атрибуты Игрока
    """

    def __init__(self, user_data: Dict, cards: Deck[Card], has_updated_game: bool = True) -> None:
        """
        Функция конструктор
        :param user_data: данные пользователя / объект модели User
        :param cards: Карты Игрока
        """
        self.user_data: Dict = user_data
        self.cards: Deck = cards
        self.__has_updated_game = has_updated_game

    @property
    def has_updated_game(self):
        value = self.__has_updated_game
        self.__has_updated_game = True
        return value

    @has_updated_game.setter
    def has_updated_game(self, value):
        self.__has_updated_game = value

    @check_if_player_is_out
    def go_on(self, game_ses: 'GameSession', card_val: str, table: 'Table', table_id: int) -> bool:
        """
        Функция подкидывания Карты
        :param game_ses: Игровая Сессия
        :param card_val: строковое представление Карты
        :param table: Стол
        :param table_id: ячейка Стола
        :return:
        Логическое подкинул: да/нет
        """
        # если переданная Карта есть в списке Карт Игрока, то удаляем ее из списка
        card: Card = self.cards.get_card_by_string(card_val)
        if card:
            # если Карту можно поставить на Стол, то удаляем ее из списка
            if table.put_card(table_id, card):
                self.cards.remove(card)
                return True
        return False

    def __eq__(self, other: Union['Player', 'Attacker', 'Defender', User]) -> bool:
        if other is not None:
            return self.user_data == other.user_data
        return False

    def __getargs__(self) -> Tuple:
        """
        Функция, возвращающая атрибуты класса
        :return:
        Кортеж атрибутов
        """
        parameters: Tuple = tuple([value for value in self.__dict__.values()])
        return parameters

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

    def __init__(self, user_data: List[User], game_index: int) -> None:
        """
        Функция конструктор
        """
        self.__cards, self.trump = self.make_deck()
        self.__players: list = self.shuffle_players(user_data)
        self.__pair = Pair(self)
        GameSession.__games[game_index] = self

    def delete(self):
        all_games = filter(lambda item: item[1] == self, GameSession.__games.items())
        for game_index, game_instance in all_games:
            index = game_index
            break
        else:
            index = None

        GameSession.__games.pop(index)

    def modified(self):
        if hasattr(self, "players"):
            for i_player in self.players:
                i_player.has_updated_game = False

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

    def remove_player(self, user: [User, Defender, Attacker]):
        player: Player = self.get_player_by_user(user)
        self.players.remove(player)
        if len(self.players) <= 1:
            self.delete()

    def get_player_by_user(self, user: [User, Defender, Attacker]) -> Player:
        for i_player in self.players:
            if i_player == user:
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

    def shuffle_players(self, users: Union[List[Dict]]) -> List[Player]:
        """
        Функция создания Игроков и раздачи Карт
        :param users: данные Игроков
        :return:
        Список Игроков
        """
        cards_for_player: Deck = Deck()
        # Сортировка Карт
        for i in range(0, CARDS_FOR_PLAYER*len(users), CARDS_FOR_PLAYER):
            cards_for_player.append(self.cards[i: i+CARDS_FOR_PLAYER])

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

    def __init__(self, lobby_index: int):
        if LobbySession.get_lobby(lobby_index) is None:
            self.__users = []
            self.__ready_to_play = False
            self.__lobby_index = lobby_index
            LobbySession.__lobbies[lobby_index] = self

    def __new__(cls, lobby_index, *args, **kwargs):
        if LobbySession.get_lobby(lobby_index) is not None:
            return LobbySession.get_lobby(lobby_index)
        return super(LobbySession, cls).__new__(cls, *args, **kwargs)

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
        self.__pair_players: List[Player] = game_ses.players[:2]
        player_classifier = zip((Attacker, Defender), self.__pair_players)

        self.attacker, self.defender = [obj_class(pair_player) for obj_class, pair_player in player_classifier]
        self.__game_ses = game_ses

    @property
    def game_ses(self):
        return self.__game_ses

    @game_ses.setter
    def game_ses(self, value):
        return

    @property
    def pair_players(self) -> List[Player]:
        return self.__pair_players

    @pair_players.setter
    def pair_players(self, value: List[Player]):
        same = all([i_player in self.__pair_players for i_player in value])
        if same:
            self.__pair_players = value

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
        if not self.attacker.is_awaken and thrower != self.defender:
            self.attacker: Attacker = Attacker(thrower)

    def leave_loser(self) -> None:
        """
        Функция, удаляющая Покрывающего Игрока, если тот все покрыл
        :return:
        """
        # Если у Покрывающего Игрока не пас, то при новой Паре, он будет Подкидывающим
        if self.defender.is_awaken:
            self.pair_players.pop()
        else:
            table_cards = self.table.cards
            self.defender.cards.extend(table_cards)

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

    def replace_players(self) -> None:
        """
        Функция, меняющая порядок Игроков
        :game_ses: Игровая Сессия
        :return:
        """
        # Первые два (или один - в зависимости от исхода Пары) игрока отправляются в конец списка
        new_players_list: List = self.game_ses.players[len(self.pair_players):]
        new_players_list.extend(self.pair_players)
        self.game_ses.players = new_players_list

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
            card for data_cell in self.values()
            for cell_key, card in data_cell.items()
            if card is None and cell_key == key
        ]
        return len(free_cells)


if __name__ == '__main__':
    pass
