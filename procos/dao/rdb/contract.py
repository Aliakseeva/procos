from datetime import date

from sqlalchemy import select, exists, ChunkedIteratorResult, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession

from procos.dao.rdb.base import BaseDAO
from procos.database.models import Contracts


class ContractDAO(BaseDAO[Contracts]):
    def __init__(self, session: AsyncSession):
        super().__init__(Contracts, session)

    async def add_contract(self, data: dict) -> Contracts:
        stmt = insert(Contracts).values(**data).returning(Contracts)
        new_contract = await self.session.execute(stmt)
        await self.session.commit()
        return new_contract.scalar()

    async def check_active_exist(self) -> bool:
        stmt = exists(Contracts.id_).where(Contracts.status == 'active').select()
        existing_active: ChunkedIteratorResult = await self.session.execute(stmt)
        return existing_active.scalar_one()

    async def get_contract_by_id(self, id_: int) -> Contracts:
        return await self._get_one_by_id(id_)

    async def get_contracts_list(self) -> list:
        return await self._get_list()

    async def get_contracts_with_status(self, status: str) -> list[Contracts]:
        stmt = select(Contracts).where(Contracts.status == status)
        contracts = await self.session.execute(stmt)
        return contracts.scalars().all()

    async def get_free_contracts_with_status(self, status: str) -> list[Contracts]:
        stmt = (
            select(Contracts)
            .where(
                and_(Contracts.status == status,
                     Contracts.project_id_ == None,         # noqa: E711
                     )
            )
            .order_by(Contracts.id_)
        )
        contracts = await self.session.execute(stmt)
        return contracts.scalars().all()

    async def sign_contract(self, new_status: str, id_: int) -> bool:
        contract = await self.get_contract_by_id(id_=id_)
        setattr(contract, 'status', new_status)
        setattr(contract, 'signed_date', date.today())
        await self.session.commit()
        await self.session.refresh(contract)
        return True

    async def update_status(self, id_: int, new_status: str) -> bool:
        contract = await self.get_contract_by_id(id_=id_)
        setattr(contract, 'status', new_status)
        await self.session.commit()
        await self.session.refresh(contract)
        return True

    async def attach_to_project(self, project_id_: int, contract_id_: int):
        contract = await self.get_contract_by_id(id_=contract_id_)
        setattr(contract, 'project_id_', project_id_)
        await self.session.commit()
        await self.session.refresh(contract)
        return True
