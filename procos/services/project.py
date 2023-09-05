from procos.dao.holder import HolderDao
from procos.database.models import Projects, Contracts
from procos.services.base import BaseSystem


class ProjectSystem(BaseSystem):
    async def list_all(self):
        """
        Lists all projects as a table.
        :return:
        """
        projects: list[Projects] = await self.dao.project.get_projects_list()
        if projects:
            print(self.data_as_table(projects))
        else:
            print('There are no projects.')

    async def create(self):
        """
        Creates a new project. Any free and ACTIVE contract required.
        :return:
        """
        active_contracts_exist = await self._check_active_contracts()
        if not active_contracts_exist:
            print(f'There is should be at least one ACTIVE contract to create the project.\n'
                  f'To make the contract ACTIVE: [contract] -> [confirm].')
            return
        await self._create()

    async def _create(self):
        """
        Creates a new project.
        :return:
        """
        print('Input the title:')
        title = input('... ')
        created: Projects | None = await self.dao.project.add_project({'title': title})
        if not created:
            print('Sorry, some error has occurred.')
            return
        print(f'Project {created.title} has been created on {created.created_date}.')

    async def attach_contract(self):
        """
        Attaches the contract to the project. Any free and ACTIVE contract required.
        :return:
        """
        contracts = await self._get_free_active_contracts()
        if not contracts:
            return
        projects = await self._get_free_projects()
        if not projects:
            return

        print(f'Choose the project to attach a contract to:')
        project_id_ = await self._select(values=projects)
        if not project_id_:
            return
        print(f'Choose the contract to attach to this project:')
        contract_id_ = await self._select(values=contracts)
        if not project_id_:
            return
        attached = await self.dao.contract.attach_to_project(project_id_=project_id_,
                                                             contract_id_=contract_id_)
        if not attached:
            print('Sorry, some error has occurred.')
            return
        print(f'The contract has been added successfully.')

    async def _get_free_active_contracts(self) -> list:
        """
        Gets a list of available contracts to attach to the project.
        :return: a list of contracts with status ACTIVE and without project.
        """
        active_contracts: list = await self.dao.contract.get_free_contracts_with_status(status='active')
        if not active_contracts:
            print('There are no ACTIVE contracts to attach to a project.\n'
                  'Create new: [contract] -> [create], or\n'
                  'confirm draft: [contract] -> [confirm].')
            return
        return active_contracts

    async def _get_free_projects(self):
        """
        Gets a list of projects available to attach a contract to.
        :return: a list of projects with no ACTIVE contracts.
        """
        free_projects = await self.dao.project.get_available_projects()
        if not free_projects:
            print('No projects or all of them have any ACTIVE contract.\n'
                  'Create a project: [project] -> [create], or\n'
                  'Complete project\'s contract: [project] -> [complete].')
            return
        return free_projects

    async def check_contract(self):
        """
        Mark the contract of the project as COMPLETED.
        :return:
        """
        active_projects = await self._get_active_projects()
        if not active_projects:
            return

        print(f'Choose the project to which the contract belongs to:')
        project_id_ = await self._select(values=active_projects)
        if not project_id_:
            return

        selected_project = self._get_project_from_list_by_id(project_id_=project_id_, projects=active_projects)
        active_contracts = self._get_active_contracts_of_project(project=selected_project)
        contracts_ids = map(lambda x: x.id_, active_contracts)

        print(f'Choose the contract in this project:')
        contract_id_ = await self._select(values=active_contracts, allowed_values=contracts_ids)
        if not contract_id_:
            return

        status_changed = await self._complete_contract(contract_id=contract_id_)
        if not status_changed:
            print('Sorry, some error has occurred.')
            return
        print(f'The status has been changed to COMPLETED.')

    async def _get_active_projects(self) -> list:
        """
        Gets a list of available projects.
        :return: a list of projects with ACTIVE contracts
        """
        active_projects = await self.dao.project.get_active_projects()
        if not active_projects:
            print('There are no projects with ACTIVE contracts.')
            return
        return active_projects

    @staticmethod
    def _get_active_contracts_of_project(project: Projects) -> list[Contracts]:
        """
        Gets a list of ACTIVE contracts belonging to the project.
        :param project: the project to extract contracts from
        :return: a list of contracts
        """
        return list(filter(lambda x: x.status == 'active', project.contracts))

    @staticmethod
    def _get_project_from_list_by_id(project_id_: int, projects: list[Projects]) -> Projects:
        """
        Get a project from projects list by filtering by ID.
        :param project_id_: ID of the project to find
        :param projects: a list of the projects
        :return: the project with desired ID
        """
        return next(filter(lambda x: x.id_ == project_id_, projects))

    async def _check_active_contracts(self) -> bool:
        """
        Check if there is any ACTIVE contracts exists.
        :return:
        """
        active_contracts_exist = await self.dao.contract.check_active_exist()
        return active_contracts_exist


async def get_project_system(dao: HolderDao) -> ProjectSystem:
    return ProjectSystem(dao=dao)
