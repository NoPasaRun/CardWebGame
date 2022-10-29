from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('postgresql+psycopg2://localhost:5433/poker_db', echo=False)
Session = sessionmaker(bind=engine)
db_session = Session()
Base = declarative_base(bind=engine)

