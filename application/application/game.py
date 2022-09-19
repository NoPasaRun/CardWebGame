import random
from inspect import stack
from typing import Dict, List, Tuple, Union
# from models import get_users


def get_users() -> List[Union[Dict]]:
    """
    Функция возвращающая информацию о пользователях
    :return:
    Список данных пользователя или объекты модели User
    """
    return [{"name": name} for name in ["Bogdan", "Dan", "Nick"]]


CARDS_IN_DECK: int = 36

HEARTS, DIAMONDS, SPADES, CLUBS = SIGNS = ("❤", "♦", "♠", "♣")
DECK: List[Tuple] = [(number, suit) for suit in SIGNS for number in range(6, 15)]
EXTRA_NUMBERS: Dict = {11: "V", 12: "D", 13: "K", 14: "T"}

PLAYER_LOW_AMOUNT, PLAYER_HIGH_AMOUNT = 2, 6
CARDS_FOR_PLAYER: int = 6


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
    __games_count: int = 0

    def __init__(self, user_data: Union[List[Dict]]) -> None:
        """
        Функция конструктор
        """
        self.__cards, self.trump = self.make_deck()
        self.__players: List = self.shuffle_players(user_data)
        self.__game_index: int = self.games_count
        self.games_count += 1

    @property
    def games_count(self) -> int:
        return GameSession.__games_count

    @games_count.setter
    def games_count(self, value):
        function = stack()[1].function
        if function.__str__() == "__init__":
            GameSession.__games_count += 1 + value*0

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
    def make_deck(cls) -> Tuple[List[Card], Card]:
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
        deck: List = [Card(*card_value, is_not_trump=trump) for card_value in deck]
        # мешаем колоду
        random.shuffle(deck)

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


class Pair:
    """
    Класс описывающий Пару Игроков (Подкидывающий/Покрывающий)
    """

    def __init__(self, game_ses: GameSession) -> None:
        """
        Функция конструктор
        :param game_ses: объект Игровой Сессии
        """
        self.table: Dict = {}
        self.__pair_index = game_ses.game_index

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

    @property
    def pair_index(self):
        return self.__pair_index

    @pair_index.setter
    def pair_index(self, val):
        return

    def do_someone_go_on(self, defender_card: Card) -> Union[Union[Attacker, Defender], bool]:
        """
        Функция, определяющая, кто ходит (или никто не ходит вообще)
        :param defender_card: Карта Покрывающего
        :return:
        Игрок, который ходит, или логическое "никто не ходит"
        """
        if defender_card and self.attacker.is_awaken and len(self.table.keys()) < CARDS_FOR_PLAYER:
            # Если до этого сходил Покрывающий, а Подкидывающий активен (не бито), то он ходит | макс 6 Карт
            self.active_player: Attacker = self.attacker
        elif not defender_card and self.defender.is_awaken and len(self.table.keys()) <= CARDS_FOR_PLAYER:
            # Если до этого сходил Подкидывающий, а Покрывающий активен (не пас), то он ходит | макс 6 Карт
            self.active_player: Defender = self.defender
        else:
            # Иначе никто не ходит
            return False
        return self.active_player

    def get_current_player(self, game_ses: GameSession) -> Union[Attacker, Defender]:
        """
        Функция, возвращающая активного игрока завершающая Игровую Пару
        :param game_ses: Игровая Сессия
        :return:
        Игрок или Игровая Сессия с измененными параметрами (атрибутами)
        """
        if game_ses.game_index == self.pair_index:
            if self.table:
                last_attacker_card: Card = list(self.table.keys())[-1]
            else:
                last_attacker_card: bool = False
            last_defender_card: Card = self.table.get(last_attacker_card, True)
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
        if not self.attacker.is_awaken and thrower.user_data != self.defender.user_data:
            self.attacker: Attacker = Attacker(thrower)

    def leave_loser(self) -> None:
        """
        Функция, удаляющая Покрывающего Игрока, если тот все покрыл
        :return:
        """
        # Если у Покрывающего Игрока не пас, то при новой Паре, он будет Подкидывающим
        if self.defender.is_awaken:
            self.pair_players.pop()

    @staticmethod
    def give_cards_to_players(players: List[Player], cards: List[Card]) -> List[Player]:
        """
        Функция, раздающая недостающие Карты Игрокам
        :param players: Список Игроков
        :param cards: Список Карт из колоды
        :return:
        Список Игроков
        """
        for i_player in players:
            cards_to_add: int = CARDS_FOR_PLAYER - len(i_player.cards)
            if cards_to_add > 0:
                i_player.cards.extend(cards[:cards_to_add])
        return players

    def replace_players(self, players: List[Player]) -> List[Player]:
        """
        Функция, меняющая порядок Игроков
        :param players: Список Игроков
        :return:
        Список Игроков
        """
        # Первые два (или один - в зависимости от исхода Пары) игрока отправляются в конец списка
        new_players_list: List = players[len(self.pair_players):]
        new_players_list.extend(self.pair_players)
        players = new_players_list

        return players

    def finish_pair(self, end_ses: GameSession) -> None:
        """
        Функция, закрывающая Пару и обновляющая данные Игровой Сессии
        :param end_ses: Игровая Сессия
        :return:
        Игровая Сессия
        """
        # Перед сменой мест Игроков в списке, важно определить нового Подкидывающего
        self.leave_loser()
        player_data: List[Player] = self.replace_players(self.give_cards_to_players(end_ses.players, end_ses.cards))
        if end_ses.game_index == self.pair_index:
            end_ses.players = player_data
