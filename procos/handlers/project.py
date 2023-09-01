from procos.cli import when, set_context, get_context
from procos.dao.holder import HolderDao
from procos.database.models import Projects


@when('project')
async def project_menu(**_):
    print('Menu ~PROJECT~\n'
          'Available commands:\n'
          '\t[create] - create new project;\n'
          '\t[add] - add a contract to the project;\n'
          '\t[check] - mark project\'s contract as completed; \n'
          '\n'
          '[back] - get back to the main menu.\n'
          )
    context = 'contract'
    set_context(context)

#
# @when('create')
# async def create_new_project(dao: HolderDao, title: str):
#     # available = await dao.contract.check_active_exist()
#     contracts = await dao.contract.get_contracts_list()
#     if not contracts:
#         print('''There is should be at least one ACTIVE contract to create the project.
#         To make the contract ACTIVE: [activate].''')
#     else:
#         created: Projects | None = await dao.project.add_project({'title': title})
#         if created:
#             print(f'Project {created.title} has been created on {created.created_date}.')
#             # # # #
#             print('''Choose the contract to attach to the project:''')
#             for contract in contracts:
#                 print(contract)
#             # await dao.project.add_project()
