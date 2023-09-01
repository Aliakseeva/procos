import asyncio
from procos.cli import cli
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from procos.handlers import *  # noqa: F401

from procos.config import load_config


def create_pool(db_url: str, echo: bool):
    engine = create_async_engine(db_url, future=True, echo=echo)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session


def run():
    """Wrapper for command line"""
    config = load_config()
    pool = create_pool(db_url=config.db.DATABASE_URL, echo=False)
    try:
        asyncio.run(cli(pool))
    except EOFError as err:
        print(err)
        print('See you soon!')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    run()
