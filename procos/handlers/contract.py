from procos.cli import when, set_context, get_context
from procos.dao.holder import HolderDao
from procos.database.models import Contracts


@when('contract')
async def contract_menu(**_):
    print('Menu ~CONTRACT~\n'
          'Available commands:\n'
          '\t[create]\n'
          '\t[confirm]\n'
          '\t[complete]\n'
          '\n'
          '[back]\n'
          )
    context = 'contract'
    set_context(context)


@when('create', context='contract')
async def create_new_contract(dao: HolderDao):
    print('Input the title:')
    try:
        title = input('... ')
    except EOFError as err:
        print('err ', err)
    else:
        created: Contracts | None = await dao.contract.add_contract({'title': title})
        if created:
            print(f'Contract \"{created.title}\" has been created on {created.created_date}.')
        else:
            print('Sorry, some error has occurred.')


@when('confirm', context='contract')
@when('complete', context='contract')
async def create_new_contract(dao: HolderDao, cmd):
    print(cmd)


# @when('change contract status STATUS', context='a')
# async def change_contract_status(dao: HolderDao, status: str):
#     pass
#
#
# @when('attach contract PROJECT_ID', context='a')
# async def attach_contract(dao: HolderDao, project_id: str):
#     pass

