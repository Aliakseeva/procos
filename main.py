import asyncio
from procos.cli import handle_command, get_prompt, get_context
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from procos.services import get_project_system, get_contract_system
from procos.dao.holder import HolderDao
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
        systems = {
            None: None,
            'contract': get_contract_system,
            'project': get_project_system,
        }
        context_system = systems[get_context()]
        cmd = input(get_prompt()).strip()
        if not cmd:
            continue
        async with pool() as session:
            # DI
            dao = HolderDao(session=session)
            system = await context_system(dao=dao) if context_system else None
            await handle_command(cmd=cmd, system=system)


def run():
    asyncio.run(main())


if __name__ == '__main__':
    """Run the program."""
    run()
