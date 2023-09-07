"""
Pool creator.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


def create_pool(db_url: str, echo: bool):
    engine = create_async_engine(db_url, future=True, echo=echo)
    pool = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return pool
