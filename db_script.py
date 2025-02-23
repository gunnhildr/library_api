from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Settings
from models.book import Base

def execute_db_script():
    """Insert test data from the file dataset.sql in the database settings.DATABASE_URL."""
    from sqlalchemy.sql import text

    settings = Settings()
    # Database setup
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    with open("dataset.sql") as f:
        statement = f.read()

    statement = text(statement)

    with engine.connect() as con:
        con.execute(statement)
        con.commit()


execute_db_script()
