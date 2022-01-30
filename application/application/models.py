from werkzeug.security import generate_password_hash
from settings import db_dir
import sqlite3
import abc


class Model(abc.ABC):

    @classmethod
    def create_filter(cls, iterable: dict) -> list:
        list_of_filters = []
        for key, value in iterable:
            if type(value) == str:
                str_value = f"'{value}'"
            elif type(value) == list:
                str_value = [(l_value if type(l_value) == int else f"'{l_value}'")
                             for l_value in value]
            else:
                str_value = value
            list_of_filters.append(f"{key} = {str_value}")
        return list_of_filters

    @classmethod
    def get(cls, object_id: int):
        with sqlite3.connect(db_dir) as connection:
            if cls.table == "users":
                sql_request = f"SELECT username, password, age, email," \
                              f" name, surname, balance, group_id, id FROM `users` WHERE id = ?;"
            else:
                sql_request = f"SELECT title, id FROM `groups` WHERE id = ?;"
            cursor = connection.cursor()
            cursor.execute(sql_request, (object_id,))
            data = cursor.fetchone()
            if data:
                return cls(*data)

    @classmethod
    def create(cls, **kwargs):
        cls.__init__(**kwargs)

    def delete(self):
        if self.id is not None:
            with sqlite3.connect(db_dir) as connection:
                sql_request = "DELETE FROM ? WHERE id = ?;"

                cursor = connection.cursor()
                cursor.execute(sql_request, (self.table, self.id,))

    def update(self, values: dict):
        if self.id is not None:
            with sqlite3.connect(db_dir) as connection:
                sql_values = ", ".join(self.create_filter(values))
                sql_request = f"UPDATE ? SET {sql_values} WHERE id = ?;"
                if sql_values:
                    cursor = connection.cursor()
                    cursor.execute(sql_request, (self.table, self.id,))


class User(Model):

    table = "users"

    def __init__(self, username: str, password: str, age: int, email: str,
                 name: str = None, surname: str = None, balance: int = 0., group_id: int = 1, id: int = None):
        super().__init__()
        self.group_id = group_id
        self.username = username
        self.password = password
        self.age = age
        self.email = email
        self.name = name
        self.surname = surname
        self.balance = balance
        self.id = id

    @classmethod
    def get_by_username(cls, username):
        with sqlite3.connect(db_dir) as connection:
            sql_request = """
                SELECT username, password, age, email, 
                name, surname, balance, group_id, id FROM `users` WHERE username = ?;
            """
            cursor = connection.cursor()
            cursor.execute(sql_request, (username,))
            data = cursor.fetchone()
            if data:
                return User(*data)

    def save(self):
        with sqlite3.connect(db_dir) as connection:
            sql_request = """
                INSERT INTO `users` (group_id, username, password, age, email, name, surname, balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """
            sql_request_get_id = "SELECT id FROM `users`;"
            cursor = connection.cursor()
            try:
                cursor.execute(sql_request, (self.group_id, self.username, generate_password_hash(self.password),
                                             self.age, self.email, self.name, self.surname, self.balance,))
                cursor.execute(sql_request_get_id)
                self.id = cursor.lastrowid
            except sqlite3.IntegrityError:
                return {"message": "Change username", "status_code": "400"}
            else:
                return {"message": "Successfully created", "status_code": "202"}


class Group(Model):
    table = "groups"

    def __init__(self, title: str = "basic", id: int = None,):
        super().__init__()
        self.title = title
        self.id = id

    def save(self):
        with sqlite3.connect(db_dir) as connection:
            sql_request = """
                INSERT INTO `groups` (title)
                VALUES (?);
            """
            cursor = connection.cursor()
            cursor.execute(sql_request, (self.title,))
            sql_request_get_id = "SELECT id FROM `groups`;"
            cursor.execute(sql_request_get_id)
            self.id = cursor.lastrowid


def create_db(create_superuser=False):
    with sqlite3.connect(db_dir) as connection:
        sql_test_request = """
            SELECT name FROM `sqlite_master`
            WHERE type='table' AND name='users';
        """
        cursor = connection.cursor()
        exist = cursor.execute(sql_test_request).fetchone()
        if not exist:
            sql_request_groups = """
                CREATE TABLE `groups` (
                    id INTEGER NOT NULL PRIMARY KEY,
                    title VARCHAR(50) NOT NULL
                );
            """
            sql_request_users = """
                CREATE TABLE `users` (
                    id INTEGER NOT NULL PRIMARY KEY,
                    group_id INTEGER DEFAULT 1,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password INTEGER NOT NULL,
                    age INTEGER NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    name VARCHAR(50) DEFAULT null,
                    surname VARCHAR(50) DEFAULT null,
                    balance FLOAT DEFAULT 0.,
                    FOREIGN KEY (group_id) REFERENCES `group` (id)
                );
            """
            cursor.execute(sql_request_groups)
            cursor.execute(sql_request_users)
            for group_name in ["basic", "advanced"]:
                Group(group_name).save()
            if create_superuser:
                User(username="NoPasaRan", password="60025102bg", age=16,
                     email="bogdanbelenesku@gmail.com", group_id=2).save()
