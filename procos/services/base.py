"""
Base system for inherit.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from tabulate import tabulate

from procos.const import TABLE_ALIGN, TABLE_STYLE
from procos.dao.holder import HolderDao
from procos.database.models import Projects, Contracts


@dataclass
class BaseSystem(ABC):
    dao: HolderDao

    @staticmethod
    def data_as_table(data: list[dict]) -> str:
        """Convert database models to human-readable tables."""
        formatted = [d.to_df() for d in data]
        return tabulate(formatted, headers='keys', tablefmt=TABLE_STYLE, stralign=TABLE_ALIGN)

    @staticmethod
    def check_id_input(user_input: str, allowed_values: list) -> int | None:
        """Check if user's input is allowed."""
        if not user_input.isdigit():
            return
        if int(user_input) not in allowed_values:
            return
        return int(user_input)

    async def _select(self, values: list[Projects | Contracts], allowed_values: list = None) -> int:
        """
        Choose the project or contract.
        :param values: a list of available projects or contracts to choose
        :return: selected ID
        """
        if allowed_values is None:
            allowed_values = map(lambda x: x.id_, values)
        print(self.data_as_table(values))
        selected_id_ = self.check_id_input(input(f'Input ID to select:\n'
                                                 f'... '), allowed_values=allowed_values)
        if not selected_id_:
            print('Wrong input.')
            return
        return selected_id_

    async def _complete_contract(self, contract_id: int) -> bool:
        completed: bool = await self.dao.contract.update_status(id_=contract_id, new_status='completed')
        return True if completed else False

    @abstractmethod
    async def list_all(self):
        raise NotImplementedError

    @abstractmethod
    async def create(self):
        raise NotImplementedError
