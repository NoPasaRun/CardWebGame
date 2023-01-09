from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('postgres+psycopg2://bogdan:YxrEvXddCIfsqgF7DNnFbnq8I498nRlh@dpg-ceu4cv5a4990mi8opjl0-a.frankfurt-postgres.render.com/poker_db')
Session = sessionmaker(bind=engine)
db_session = Session()
Base = declarative_base(bind=engine)

