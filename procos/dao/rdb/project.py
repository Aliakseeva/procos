from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, ChunkedIteratorResult, insert

from procos.dao.rdb.base import BaseDAO
from procos.database.models import Projects


class ProjectDAO(BaseDAO[Projects]):
    def __init__(self, session: AsyncSession):
        super().__init__(Projects, session)

    async def get_project_by_id(self, id_: int):
        return await self._get_one_by_id(id_)

    async def get_projects_list(self):
        return await self._get_list()

    async def add_project(self, data: dict):
        stmt = insert(Projects).values(**data).returning(Projects)
        new_project = await self.session.execute(stmt)
        await self.session.commit()
        return new_project.scalar()
