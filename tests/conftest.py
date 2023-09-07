import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.command import upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import close_all_sessions, sessionmaker

from procos.dao.holder import HolderDao
from procos.services.contract import ContractSystem, get_contract_system
from procos.services.project import ProjectSystem, get_project_system


@pytest_asyncio.fixture
async def session(pool: sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with pool() as session_:
        yield session_


@pytest.fixture(scope="session")
def postgres_url() -> str:
    return "postgresql+asyncpg://postgres:postgres@localhost:5435/postgres"


@pytest.fixture(scope="session")
def pool(postgres_url: str) -> Generator[sessionmaker, None, None]:
    engine = create_async_engine(url=postgres_url)
    pool_: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine, expire_on_commit=False, autoflush=False
    )
    yield pool_
    close_all_sessions()


@pytest_asyncio.fixture
async def dao(session: AsyncSession) -> AsyncGenerator:
    dao_ = HolderDao(session=session)
    yield dao_
    await truncate_all(dao=dao_)


@pytest.fixture(scope="session")
def path():
    path_ = Path(__file__).parent
    return path_


@pytest.fixture(scope="session")
def event_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@pytest_asyncio.fixture(scope="function")
async def test_contract(dao: HolderDao) -> ContractSystem:
    contract = await get_contract_system(dao=dao)
    return contract


@pytest_asyncio.fixture(scope="function")
async def test_project(dao: HolderDao) -> ProjectSystem:
    project = await get_project_system(dao=dao)
    return project


@pytest.fixture(scope="session")
def alembic_config(postgres_url: str, path: Path) -> AlembicConfig:
    alembic_cfg = AlembicConfig(str(path.parent / "alembic.ini"))
    alembic_cfg.set_main_option(
        "script_location",
        str(path.parent / "procos" / "database" / "migrations"),
    )
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_url)
    return alembic_cfg


@pytest.fixture(scope="session", autouse=True)
def upgrade_db_schema(alembic_config: AlembicConfig):
    upgrade(alembic_config, "head")


async def truncate_all(dao: HolderDao):
    await dao.contract.delete_all()
    await dao.project.delete_all()
    await dao.commit()
