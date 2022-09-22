import random
from typing import Dict, List, Tuple, Union

from application.application.models import User


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
    def __getitem__(self, index):
        output = super().__getitem__(index)
        values = [output] if not isinstance(output, list) else output
        for val in values:
            self.remove(val)
        return output

    def shuffle(self):
        shuffled_deck = self.copy()
        random_indexes = list(range(len(self)))

        random.shuffle(random_indexes)
        for index, random_index in enumerate(random_indexes):
            self[index] = shuffled_deck[random_index]

    def __str__(self):
        return str([str(card) for card in self])


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
        if is_not_trump:
            # если карта не выбрана козырем, но масть совпадает с мастью козыря, то карта - козырь
            self.is_trump = sign == is_not_trump.suit
        else:
            # если карта козырь, то "не козырная карта" меняется на "козырная карта
            self.is_trump = not is_not_trump

    def __str__(self) -> str:
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


class Player:
    """
    Класс, описывающий атрибуты Игрока
    """

    def __init__(self, user_data: Dict, cards: List[Card]) -> None:
        """
        Функция конструктор
        :param user_data: данные пользователя / объект модели User
        :param cards: Карты Игрока
        """
        self.user_data: Dict = user_data
        self.cards: List = cards

    def __eq__(self, other: Union['Player', 'Attacker', 'Defender', User]) -> bool:
        return self.user_data == other.user_data

    def __getargs__(self) -> Tuple:
        """
        Функция, возвращающая атрибуты класса
        :return:
        Кортеж атрибутов
        """
        parameters: Tuple = tuple([value for value in self.__dict__.values()])
        return parameters


class Attacker(Player):
    """
    Класс, описывающий поведения Игрока-Подкидывающего
    """

    def __init__(self, player: Player) -> None:
        """
        Функция конструктор
        :param player:
        """
        args: Tuple = player.__getargs__()
        super().__init__(*args)
        # атрибут, показывающий логическое "бито"
        self.__is_awaken: bool = True

    @property
    def is_awaken(self) -> bool:
        return self.__is_awaken

    def go_on(self, attacker_card: Card) -> bool:
        """
        Функция подкидывания Карты
        :param attacker_card: Карта
        :return:
        Логическое подкинул: да/нет
        """
        # если переданная Карта есть в списке Карт Игрока-Подкидающего, то удаляем ее из списка
        if attacker_card in self.cards:
            self.cards.remove(attacker_card)
            return True
        return False


class Defender(Player):
    """
    Класс, описывающий поведение Игрока-Покрывающего
    """

    def __init__(self, player: Player) -> None:
        """
        Функция конструктор
        :param player:
        """
        args: Tuple = player.__getargs__()
        super().__init__(*args)
        # атрибут, показывающий логическое "пас"
        self.__is_awaken = True

    @property
    def is_awaken(self) -> bool:
        return self.__is_awaken

    @is_awaken.setter
    def is_awaken(self, value: bool):
        self.__is_awaken = value

    def go_on(self, attacker_card: Card, defender_card: Card) -> bool:
        """
        Функция покрывания Карты
        :param attacker_card: Карта подкидывающего
        :param defender_card: Карта покрывающего
        :return:
        Логическое покрыл: да/нет
        """
        # если покрывающая Карта больше подкидывающей, то удаляем ее из списка
        if defender_card > attacker_card:
            self.cards.remove(defender_card)
            return True
        return False


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
        self.__players: List = self.shuffle_players(user_data)
        self.__game_index: int = game_index
        self.__pair = Pair(self)
        self.__games[game_index] = self

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
    def game_index(self):
        return self.__game_index

    @game_index.setter
    def game_index(self, val):
        return

    @property
    def players(self) -> List[Player]:
        return self.__players

    @property
    def cards(self) -> List[Card]:
        return self.__cards

    @players.setter
    def players(self, new_list_of_players: List[Player]) -> None:
        self.__players: List = new_list_of_players

    @cards.setter
    def cards(self, used_cards) -> None:
        set_of_cards = set(self.__cards)
        set_of_cards.difference_update(used_cards)
        self.__cards = list(set_of_cards)

    @classmethod
    def make_deck(cls) -> Tuple[Deck[Card], Card]:
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
        deck: Deck = Deck([Card(*card_value, is_not_trump=trump) for card_value in deck])
        # мешаем колоду
        deck.shuffle()

        deck.append(trump)
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
        cards_for_player: List = []
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


def compair_pair_and_session(func):
    def wrapper(*args, **kwargs):
        self: Pair = args[0]
        try:
            game_session: GameSession = args[1]
        except IndexError:
            game_session: GameSession = kwargs.get("game_ses", None)
        if isinstance(game_session, GameSession):
            if self == game_session.pair:
                return func(*args, **kwargs)
            else:
                raise PermissionError("Game.pair and Pair are not the same")
        return func(*args, **kwargs)
    return wrapper


class Table:
    def __init__(self):
        self.data = {key: {OFF: None, DEF: None} for key in range(1, 7)}

    def get_last_def_card(self) -> Union[Card, None]:
        values = [(data_cell[OFF], data_cell[DEF]) for data_cell in self.data.values()]
        for off_card, def_card in reversed(values):
            if def_card is not None:
                return def_card
        else:
            return None

    def get_items(self) -> List[Tuple[int, Tuple]]:
        items = [(index, (data_cell[OFF], data_cell[DEF])) for index, data_cell in self.data.items()]
        return items

    @property
    def free_cells(self) -> int:
        values = list(self.data.values())
        return values.count(None)


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
        # Первым ходит Подкидывающий - он активный
        self.__active_player: Union[Defender, Attacker] = self.attacker

    @property
    def active_player(self) -> Union[Defender, Attacker]:
        return self.__active_player

    @active_player.setter
    def active_player(self, player: Union[Attacker, Defender]) -> None:
        self.__active_player = player

    @property
    def pair_players(self) -> List[Player]:
        return self.__pair_players

    def do_someone_go_on(self, defender_card: Union[Card, None]) -> Union[Union[Attacker, Defender], bool]:
        """
        Функция, определяющая, кто ходит (или никто не ходит вообще)
        :param defender_card: Карта Покрывающего
        :return:
        Игрок, который ходит, или логическое "никто не ходит"
        """
        free_cells = self.table.free_cells
        if defender_card is not None and self.attacker.is_awaken and free_cells > 1:
            # Если до этого сходил Покрывающий, а Подкидывающий активен (не бито), то он ходит | макс 6 Карт
            self.active_player: Attacker = self.attacker
        elif defender_card is None and self.defender.is_awaken and free_cells >= 1:
            # Если до этого сходил Подкидывающий, а Покрывающий активен (не пас), то он ходит | макс 6 Карт
            self.active_player: Defender = self.defender
        else:
            # Иначе никто не ходит
            return False
        return self.active_player

    @compair_pair_and_session
    def get_current_player(self, game_ses: GameSession) -> Union[Attacker, Defender]:
        """
        Функция, возвращающая активного игрока завершающая Игровую Пару
        :param game_ses: Игровая Сессия
        :return:
        Игрок или Игровая Сессия с измененными параметрами (атрибутами)
        """
        last_defender_card = self.table.get_last_def_card()
        # Получаем текущего пользователя
        current_player: Union[Union[Attacker, Defender], bool] = self.do_someone_go_on(last_defender_card)
        if current_player:
            return current_player
        else:
            # Заканчиваем Игровую Пару
            self.finish_pair(game_ses)

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

    @compair_pair_and_session
    def give_cards_to_players(self, game_ses: GameSession) -> None:
        """
        Функция, раздающая недостающие Карты Игрокам
        :game_ses: Игровая Сессия
        :return:
        """
        for i_player in game_ses.players:
            cards_to_add: int = CARDS_FOR_PLAYER - len(i_player.cards)
            if cards_to_add > 0:
                cards_to_add: List[Card] = game_ses.cards[:cards_to_add]
                i_player.cards.extend(cards_to_add)

    @compair_pair_and_session
    def replace_players(self, game_ses: GameSession) -> None:
        """
        Функция, меняющая порядок Игроков
        :game_ses: Игровая Сессия
        :return:
        """
        # Первые два (или один - в зависимости от исхода Пары) игрока отправляются в конец списка
        new_players_list: List = game_ses.players[len(self.pair_players):]
        new_players_list.extend(self.pair_players)
        game_ses.players = new_players_list

    @compair_pair_and_session
    def finish_pair(self, game_ses: GameSession) -> None:
        """
        Функция, закрывающая Пару и обновляющая данные Игровой Сессии
        :param game_ses: Игровая Сессия
        :return:
        Игровая Сессия
        """
        # Перед сменой мест Игроков в списке, важно определить нового Подкидывающего
        self.leave_loser()
        self.give_cards_to_players(game_ses)
        self.replace_players(game_ses)
