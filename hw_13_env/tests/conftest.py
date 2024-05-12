# conftest.py
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from main import app
from src.entity.models import Base, User
from src.database.db import get_db
from src.services.auth import auth_service

SQLALCHEMY_DATABASE = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {"username": "tester", "email": "tester@example.com", "password": "0123456"}


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        hash_password = auth_service.get_password_hash(test_user["password"])
        current_user = User(username=test_user["username"], email=test_user["email"], password=hash_password,
                            confirmed=True, role="admin")
        session.add(current_user)
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def session():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)