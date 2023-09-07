import json
import os
from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from app.core.config import BASEDIR
from app.db.cache import get_cache
from app.db.database import get_session
from app.db.models import Dish, Menu, Submenu
from app.main import app


@dataclass
class FakeCacheService:
    """Fake cache service."""

    storage: dict = field(default_factory=dict)

    async def set(self, key: str, value: Any, **kwargs):
        """Sets an object to the cache."""
        self.storage[key] = value

    async def get(self, key: str):
        """Gets an object from the cache."""
        return self.storage.get(key)

    async def delete(self, key: str):
        """Removes an object from the cache."""
        return self.storage.pop(key, None)


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        app=app,
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def session_db_override(test_session) -> None:
    def get_test_session() -> Generator[Generator, None, None]:
        yield test_session

    app.dependency_overrides[get_session] = get_test_session


@pytest_asyncio.fixture(scope="function")
async def test_session() -> AsyncSession:
    async_engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        future=True,
    )
    async_session = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        async with async_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

        yield session

    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def cache_override(test_cache) -> None:
    def get_test_cache() -> Generator[Generator, None, None]:
        yield test_cache

    app.dependency_overrides[get_cache] = get_test_cache


@pytest_asyncio.fixture(scope="function")
async def test_cache() -> FakeCacheService:
    redis = FakeCacheService()
    return redis


@pytest.fixture(autouse=True)
def reset_dependency_overrides() -> Generator:
    yield
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def test_data() -> dict:
    path = os.path.join(BASEDIR, "tests/data/test_data.json")
    with open(path) as file:
        return json.loads(file.read())


@pytest_asyncio.fixture(autouse=True)
async def initial_db_data(test_session: AsyncSession) -> dict:
    path = os.path.join(BASEDIR, "tests/data/test_preload_db_data.json")
    with open(path) as file:
        db_data = json.loads(file.read())
    for menu in db_data["fill_menu"]:
        menu = Menu(**db_data["fill_menu"][menu])
        test_session.add(menu)
        await test_session.commit()
    for submenu in db_data["fill_submenu"]:
        submenu = Submenu(**db_data["fill_submenu"][submenu])
        test_session.add(submenu)
        await test_session.commit()
    for submenu in db_data["fill_submenu_m2"]:
        submenu = Submenu(**db_data["fill_submenu_m2"][submenu])
        test_session.add(submenu)
        await test_session.commit()
    for dish in db_data["fill_dish"]:
        dish = Dish(**db_data["fill_dish"][dish])
        test_session.add(dish)
        await test_session.commit()
    for dish in db_data["fill_dish_m2"]:
        dish = Dish(**db_data["fill_dish_m2"][dish])
        test_session.add(dish)
        await test_session.commit()
    return db_data
