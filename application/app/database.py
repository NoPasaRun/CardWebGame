from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


connection_address = 'postgresql+psycopg2://bogdan:YxrEvXddCIfsqgF7DNnFbnq8I498nRlh@' \
                     'dpg-ceu4cv5a4990mi8opjl0-a.frankfurt-postgres.render.com/poker_db'

engine = create_engine(connection_address, pool_pre_ping=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base(bind=engine)

