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





def run():
    asyncio.run(main())


if __name__ == '__main__':
    """Run the program."""
    run()
