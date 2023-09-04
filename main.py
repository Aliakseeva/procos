import asyncio
from procos.cli import handle_command, get_prompt
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from procos.handlers import *  # noqa: F401

from procos.config import load_config


def create_pool(db_url: str, echo: bool):
    engine = create_async_engine(db_url, future=True, echo=echo)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session


async def main():
    """Wrapper for command line"""
    config = load_config()
    pool = create_pool(db_url=config.db.DATABASE_URL, echo=False)

    while True:
        cmd = input(get_prompt()).strip()
        if not cmd:
            continue
        async with pool() as session:
            dao = HolderDao(session=session)
            await handle_command(dao, cmd)


def run():
    asyncio.run(main())


if __name__ == '__main__':
    """Run the program."""
    run()

