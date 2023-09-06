"""
System for managing contracts.
"""
from procos.dao.holder import HolderDao
from procos.database.models import Contracts
from procos.services.base import BaseSystem


class ContractSystem(BaseSystem):
    async def list_all(self) -> list:
        """
        Lists all contracts as a table.
        :return:
         """
        contracts: list[Contracts] = await self.dao.contract.get_contracts_list()
        if contracts:
            print(self.data_as_table(contracts))
        else:
            print('There is not any contract exists.')

    async def create(self):
        """
        Creates a new contract.
        :return:
        """
        print('Input the title:')
        title = input('... ')
        created: Contracts | None = await self.dao.contract.add_contract({'title': title})
        if not created:
            print('Sorry, some error has occurred.')
            return
        print(f'Contract \"{created.title}\" has been created on {created.created_date}.')

    async def change_contract_status(self, cmd: str):
        """
        Changes a status of the contract.
        :param cmd: command passing by the user
        :return:
        """
        current_status = self.get_current_status(cmd=cmd)
        new_status = self.get_new_status(cmd=cmd)
        contracts_list: list[Contracts] = await self._choose_contract(status=current_status)
        if not contracts_list:
            print(f'No available contracts to make the status \"{cmd}\".')
            return

        print(f'Available contracts:')
        contract_id_ = await self._select(values=contracts_list)
        if not contract_id_:
            return
        await self._change_status(id_=contract_id_, contracts_list=contracts_list, cmd=cmd, new_status=new_status)

    @staticmethod
    def get_current_status(cmd: str):
        """Gets a current status of contract. Based on passing command."""
        return 'draft' if cmd == 'confirm' else 'active'

    @staticmethod
    def get_new_status(cmd: str):
        """Gets next status of contract. Based on passing command."""
        return 'active' if cmd == 'confirm' else 'completed'

    async def _confirm_contract(self, contract_id: int) -> bool:
        """
        Makes contract CONFIRMED -- changes the status to ACTIVE.
        :param contract_id: ID of contract to confirm
        :return: True if status changed successfully
        """
        confirmed: bool = await self.dao.contract.sign_contract(new_status='active', id_=contract_id)
        return True if confirmed else False

    async def _choose_contract(self, status: str) -> list:
        """
        Gets the contract list, filtered by status.
        :param status: state of the contract to filter by
        :return: list of filtered by status contracts
        """
        contracts_list = await self.dao.contract.get_contracts_with_status(status=status)
        return contracts_list

    async def _change_status(self, id_: int, contracts_list: list, cmd: str, new_status: str):
        """
        Check if it is possible to change contract status.
        :param id_: ID of the contract to change its status
        :param contracts_list: a list of contracts available to status change
        :param cmd: a command passing by the user
        :param new_status: new status based on the command
        :return:
        """
        contract_to_change: Contracts | None = await self.dao.contract.get_contract_by_id(id_=id_)
        if contract_to_change and contract_to_change in contracts_list:
            status_changed = await self._change_status_hub(cmd=cmd, contract_id=contract_to_change.id_)
            if status_changed:
                print(f'The status of \"{contract_to_change.title}\" '
                      f'has been changed to {new_status}.')
        else:
            print(f'There is no such contract to change the status to {new_status}.')

    async def _change_status_hub(self, cmd: str, contract_id: int) -> bool:
        """
        Chooses the strategy of changing contracts status.
        :param cmd: command passing by user
        :param contract_id: ID of contract to change a status
        :return: True if status changed successfully
        """
        hub = {
            'confirm': self._confirm_contract,
            'complete': self._complete_contract,
        }
        func = hub[cmd]
        status_changed = await func(dao=self.dao, contract_id=contract_id)
        return status_changed


async def get_contract_system(dao: HolderDao) -> ContractSystem:
    return ContractSystem(dao=dao)
