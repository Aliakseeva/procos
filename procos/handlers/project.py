from procos.cli import when, set_context, get_context
from procos.dao.holder import HolderDao
from procos.database.models import Projects
from procos.services.general import data_as_markdown


@when('project', context=None)
async def project_menu(**_):
    print('Menu ~PROJECT~\n'
          'Available commands:\n'
          '\t[list] - list all projects;\n'
          '\t[create] - create new project;\n'
          '\t[attach] - attach a contract to the project;\n'
          '\t[check] - mark project\'s contract as completed; \n'
          '\n'
          '[back] - get back to the main menu.\n'
          )
    context = 'project'
    set_context(context)


@when('list', context='project')
async def list_all_contracts(dao: HolderDao, **_):
    projects: list[Projects] = await dao.project.get_projects_list()
    if projects:
        print(data_as_markdown([project.to_df() for project in projects]))
    else:
        print('There is not any projects exists.')


@when('create', context='project')
async def create_new_project(dao: HolderDao, **_):
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
    if project_id_ is None:
        active_contract_exits = await check_active_contracts(dao=dao)
        if active_contract_exits:
            projects = await dao.project.get_projects_list()  # TODO: не во все проекты можно добавить контракт
            if projects:
                print(f'Choose the project to attach a contract to:')
                for project in projects:
                    print(project)
                project_id_ = int(input(f'Input the project ID:\n'
                                        f'... '))
            else:
                print('There is should be at least one project created.\n'
                      'To create a project: [project] -> [create].')
                return
        else:
            return

    print(f'Choose the contract to attach to this project:')
    active_contracts = await dao.contract.get_contracts_with_status(status='active')
    for contract in active_contracts:
        print(contract)
    contract_id_ = int(input(f'Input the contract ID:\n'
                             f'... '))
    attached = await dao.contract.attach_to_project(project_id_=project_id_,
                                                    contract_id_=contract_id_)
    if attached:
        print(f'The contract has been added successfully.')


@when('back', context='project')
async def back(**_):
    context = None
    set_context(context)


async def check_active_contracts(dao: HolderDao):
    active_contracts = await dao.contract.check_active_exist()
    if not active_contracts:
        print(f'There is should be at least one ACTIVE contract to create the project.\n'
              f'To make the contract ACTIVE: [contract] -> [confirm].')
        return False
    return True
