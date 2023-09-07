"""
Data access object for contracts..
"""
from datetime import date

from sqlalchemy import ChunkedIteratorResult, and_, exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from procos.dao.rdb.base import BaseDAO
from procos.database.models import Contracts


class ContractDAO(BaseDAO[Contracts]):
    def __init__(self, session: AsyncSession):
        super().__init__(Contracts, session)

    async def add_contract(self, data: dict) -> Contracts:
        """
        :param data: fields of new contract
        :return: created contract instance
        """
        stmt = insert(Contracts).values(**data).returning(Contracts)
        new_contract = await self.session.execute(stmt)
        await self.session.commit()
        return new_contract.scalar()

    async def check_free_active_exist(self) -> bool:
        """

        :return: True if free and active contract exists
        """
        stmt = (
            exists(Contracts.id_)
            .where(and_(
                Contracts.status == "active",
                Contracts.project_id_ == None,  # noqa: E711
            ))
            .select()
        )
        existing_active: ChunkedIteratorResult = await self.session.execute(stmt)
        return existing_active.scalar_one()

    async def get_contract_by_id(self, id_: int) -> Contracts:
        return await self._get_one_by_id(id_)

    async def get_contracts_list(self) -> list[Contracts]:
        return await self._get_list()

    async def get_contracts_with_status(self, status: str) -> list[Contracts]:
        """

        :param status: status of contracts to filter by
        :return: list of contracts with passed status
        """
        stmt = select(Contracts).where(Contracts.status == status).order_by(Contracts.id_)
        contracts = await self.session.execute(stmt)
        return contracts.scalars().all()

    async def get_free_contracts_with_status(self, status: str) -> list[Contracts]:
        """

        :param status: status of contracts to filter by
        :return: list of active contracts with passed status
        """
        stmt = (
            select(Contracts)
            .where(
                and_(
                    Contracts.status == status,
                    Contracts.project_id_ == None,  # noqa: E711
                )
            )
            .order_by(Contracts.id_)
        )
        contracts = await self.session.execute(stmt)
        return contracts.scalars().all()

    async def sign_contract(self, new_status: str, id_: int) -> bool:
        """

        :param new_status: status to set to the contract
        :param id_: ID of contract to mark as signed
        :return: True on success
        """
        contract = await self.get_contract_by_id(id_=id_)
        setattr(contract, "status", new_status)
        setattr(contract, "signed_date", date.today())
        await self.session.commit()
        await self.session.refresh(contract)
        return True

    async def update_status(self, id_: int, new_status: str) -> bool:
        """

        :param id_: ID of contract to update its status
        :param new_status: status to set to the contract
        :return: True on success
        """
        contract = await self.get_contract_by_id(id_=id_)
        setattr(contract, "status", new_status)
        await self.session.commit()
        await self.session.refresh(contract)
        return True

    async def attach_to_project(self, project_id_: int, contract_id_: int):
        """

        :param project_id_: ID of the project to which attach the contract
        :param contract_id_: ID of the contract to attach to selected project
        :return: True on success
        """
        contract = await self.get_contract_by_id(id_=contract_id_)
        setattr(contract, "project_id_", project_id_)
        await self.session.commit()
        await self.session.refresh(contract)
        return True
