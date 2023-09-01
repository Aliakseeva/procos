from sqlalchemy.ext.asyncio import AsyncSession

from .rdb import ContractDAO, ProjectDAO


class HolderDao:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.contract = ContractDAO(self.session)
        self.project = ProjectDAO(self.session)

    async def commit(self):
        await self.session.commit()
