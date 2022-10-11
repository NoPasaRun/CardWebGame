from typing import List

from sqlalchemy import Column, String, Integer, Float, select
from werkzeug.security import generate_password_hash, check_password_hash
from application.application.database import Base, db_session


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id: int = Column(Integer(), primary_key=True)
    username: str = Column(String(256), unique=True, nullable=False)
    password: str = Column(String(256), nullable=False)
    balance: float = Column(Float(), default=0.)

    def __repr__(self):
        return self.username

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    @property
    def user_data(self):
        return self

    @classmethod
    def get(cls, user_id: int):
        output = db_session.execute(select(cls).where(cls.id == user_id))
        user = output.fetchone()
        if user:
            return user[0]

    @classmethod
    def get_by_username(cls, username: str) -> 'User':
        output = db_session.execute(select(cls).where(cls.username == username))
        user = output.fetchone()
        if user:
            return user[0]

    @classmethod
    def all(cls) -> List['User']:
        output = db_session.execute(select(cls))
        users = [user for row in output.fetchall() for user in row]
        return users


if __name__ == '__main__':
    Base.metadata.create_all()
