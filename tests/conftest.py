from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def test_app() -> Generator[TestClient, None, None]:
    """Fixture to yield a test instance of an app."""
    from main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def db_session() -> Generator[Session, None, None]:
    """Fixture to yield a test database session."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from config import Settings
    from models.book import Base

    settings = Settings()
    # Database setup
    engine = create_engine(settings.DATABASE_URL)

    connection = engine.connect()
    transaction = connection.begin()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session
    transaction.rollback()
