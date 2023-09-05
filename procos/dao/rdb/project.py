from sqlalchemy import select, insert, or_
from sqlalchemy.ext.asyncio import AsyncSession

from procos.dao.rdb.base import BaseDAO
from procos.database.models import Projects, Contracts


class ProjectDAO(BaseDAO[Projects]):
    def __init__(self, session: AsyncSession):
        super().__init__(Projects, session)

    async def get_project_by_id(self, id_: int):
        return await self._get_one_by_id(id_)

    async def get_projects_list(self):
        return await self._get_list()

    async def get_available_projects(self) -> list[Projects]:
        """Get a list of projects with NO active contracts."""
        stmt = (
            select(Projects)
            .where(
                or_(
                    ~Projects.contracts.any(Contracts.status == 'active'),
                    Projects.contracts == None,     # noqa: E711
                )
            )
        )
        projects = await self.session.execute(stmt)
        return projects.scalars().all()

    async def get_active_projects(self) -> list[Projects]:
        """Get a list of projects WITH active contracts."""
        stmt = (
            select(Projects)
            .where(
                Projects.contracts.any(Contracts.status == 'active')
            )
        )
        projects = await self.session.execute(stmt)
        return projects.scalars().all()

    async def add_project(self, data: dict):
        stmt = insert(Projects).values(**data).returning(Projects)
        new_project = await self.session.execute(stmt)
        await self.session.commit()
        return new_project.scalar()
