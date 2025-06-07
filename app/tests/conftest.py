import pytest
from fastapi.testclient import TestClient
from api import app
from sqlmodel import Session, create_engine

from database.config import get_settings

settings = get_settings()
DATABASE_URL = settings.DATABASE_URL_psycopg


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        DATABASE_URL,
    )
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture():
    client = TestClient(app)
    yield client