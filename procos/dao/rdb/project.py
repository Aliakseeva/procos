from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, ChunkedIteratorResult, insert, or_

from procos.dao.rdb.base import BaseDAO
from procos.database.models import Projects, Contracts


class ProjectDAO(BaseDAO[Projects]):
    def __init__(self, session: AsyncSession):
        super().__init__(Projects, session)

    async def get_project_by_id(self, id_: int):
        return await self._get_one_by_id(id_)

    async def get_projects_list(self):
        return await self._get_list()

    async def get_free_projects(self) -> list[Projects]:
        """Get a list of projects with no ACTIVE contracts."""
        # stmt = select(Projects).where(or_(Projects.contracts is []))  # TODO
        stmt = select(Projects).where(Projects.contracts is None)  # TODO
        projects = await self.session.execute(stmt)
        return projects.scalars().all()

    async def add_project(self, data: dict):
        stmt = insert(Projects).values(**data).returning(Projects)
        new_project = await self.session.execute(stmt)
        # await self.session.commit()
        return new_project.scalar()
