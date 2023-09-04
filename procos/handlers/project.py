from typing import Iterable

from procos.cli import when, set_context, get_context
from procos.dao.holder import HolderDao
from procos.database.models import Projects
from procos.services.general import data_as_table, check_id_input


@when('project', context=None)
async def project_menu(**_):
    """show project menu."""
    context = 'project'
    set_context(context)


@when('list', context='project')
async def list_all_projects(dao: HolderDao, **_):
    """list all projects."""
    projects: list[Projects] = await dao.project.get_projects_list()
    if projects:
        print(data_as_table(projects))
    else:
        print('There are no projects.')


@when('create', context='project')
async def create_new_project(dao: HolderDao, **_):
    """create a new project."""
    # available = await dao.contract.check_active_exist()
    active_contract_exist = await check_active_contracts(dao=dao)
    if active_contract_exist:
        print('Input the title:')
        title = input('... ')
        created: Projects | None = await dao.project.add_project({'title': title})
        if created:
            print(f'Project {created.title} has been created on {created.created_date}.')

        await attach_contract_to_project(dao=dao, project_id_=created.id_)


@when('attach', context='project')
async def attach_contract_to_project(dao: HolderDao, project_id_: int = None, **_):
    """attach a contract to the project."""
    active_contracts = await dao.contract.get_free_contracts_with_status(status='active')
    if not active_contracts:
        print('There are no ACTIVE contracts to attach to a project.\n'
              'Create new: [contract] -> [create], or\n'
              'confirm draft: [contract] -> [confirm].')
        return

    if project_id_ is None:
        active_contract_exits = await check_active_contracts(dao=dao)
        if active_contract_exits:
            free_projects = await dao.project.get_available_projects()
            if free_projects:
                print(f'Choose the project to attach a contract to:')
                print(data_as_table(free_projects))
                allowed_values = map(lambda x: x.id_, free_projects)
                project_id_ = check_id_input(input(f'Input the project ID:\n'
                                                   f'... '), allowed_values=allowed_values)
                if not project_id_:
                    print('Wrong input.')
                    return
            else:
                print('No projects or all of them have any ACTIVE contract.\n'
                      'Create a project: [project] -> [create], or\n'
                      'Complete project\'s contract: [project] -> [complete].')
                return
        else:
            return

    print(f'Choose the contract to attach to this project:')
    print(data_as_table(active_contracts))
    allowed_values = map(lambda x: x.id_, active_contracts)
    contract_id_ = check_id_input(input(f'Input the contract ID:\n'
                                        f'... '), allowed_values=allowed_values)
    if not contract_id_:
        print('Wrong input.')
        return
    await dao.commit()      # на случай, если выбор договора был прерван
    attached = await dao.contract.attach_to_project(project_id_=project_id_,
                                                    contract_id_=contract_id_)
    if attached:
        print(f'The contract has been added successfully.')


@when('back', context='project')
async def back(**_):
    """get back to the main menu."""
    context = None
    set_context(context)


async def check_active_contracts(dao: HolderDao):
    active_contracts = await dao.contract.check_active_exist()
    if not active_contracts:
        print(f'There is should be at least one ACTIVE contract to create the project.\n'
              f'To make the contract ACTIVE: [contract] -> [confirm].')
        return False
    return True
