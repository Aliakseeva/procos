"""
Base DAO for inheritance.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy import Result, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from procos.database.models import Base

Model = TypeVar("Model", bound=Base, covariant=True, contravariant=False)


@dataclass
class BaseDAO(Generic[Model]):
    model: type[Model]
    session: AsyncSession

    async def _get_one_by_id(self, id_: int) -> Model:
        one = await self.session.execute(select(self.model).where(self.model.id_ == id_))
        return one.scalar()

    async def _get_list(self) -> Sequence[Model]:
        list_: Result[Model] = await self.session.execute(select(self.model))
        return list_.scalars().all()

    async def delete_all(self):
        await self.session.execute(delete(self.model))
