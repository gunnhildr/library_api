from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Settings
from models.book import Base

settings = Settings()
# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables
Base.metadata.create_all(bind=engine)


def execute_db_script():
    from sqlalchemy.sql import text

    with open("dataset.sql") as f:
        statement = f.read()

    statement = text(statement)

    with engine.connect() as con:
        con.execute(statement)
        con.commit()


execute_db_script()
