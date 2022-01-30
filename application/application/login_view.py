from models import User
from flask_login import LoginManager


class LoginUser(LoginManager):

    def fromDB(self, user_id):
        self.__user = User.get(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user.id)
