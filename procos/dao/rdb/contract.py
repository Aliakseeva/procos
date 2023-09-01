from sqlalchemy import select, exists, ChunkedIteratorResult, insert
from sqlalchemy.ext.asyncio import AsyncSession

from procos.dao.rdb.base import BaseDAO
from procos.database.models import Contracts


class ContractDAO(BaseDAO[Contracts]):
    def __init__(self, session: AsyncSession):
        super().__init__(Contracts, session)

    async def check_active_exist(self) -> bool:
        stmt = exists(self.model.id_).where(self.model.status == 'active').select()
        existing_active: ChunkedIteratorResult = await self.session.execute(stmt)
        return existing_active.scalar_one()

    async def get_contract_by_id(self, id_: int):
        return await self._get_one_by_id(id_)

    async def get_contracts_list(self):
        return await self._get_list()

    async def add_contract(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        new_contract = await self.session.execute(stmt)
        return new_contract.scalar()

    async def update_status(self, id_: int, new_status: str):
        contract = self.get_contract_by_id(id_=id_)
        setattr(contract, 'status', new_status)
        await self.session.commit()
        await self.session.refresh(contract)

