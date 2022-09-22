from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('postgresql+psycopg2://bogdan:60025102bg@127.0.0.1:5432/poker_db', echo=True)
Session = sessionmaker(bind=engine)
db_session = Session()
Base = declarative_base(bind=engine)

