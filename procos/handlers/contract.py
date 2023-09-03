from procos.cli import when, set_context, get_context
from procos.dao.holder import HolderDao
from procos.database.models import Contracts
from pandas import DataFrame
from procos.services.general import data_as_markdown


@when('contract', context=None)
async def contract_menu(**_):
    print('Menu ~CONTRACT~\n'
          'Available commands:\n'
          '\t[list] - list all contracts;\n'
          '\t[create] - create new contract;\n'
          '\t[confirm] - switch contract status to ACTIVE;\n'
          '\t[complete] - switch contract status to COMPLETED;\n'
          '\n'
          '[back] - get back to the main menu.\n'
          )
    context = 'contract'
    set_context(context)


@when('list', context='contract')
async def list_all_contracts(dao: HolderDao, **_):
    contracts: list[Contracts] = await dao.contract.get_contracts_list()
    if contracts:
        print(data_as_markdown([contract.to_df() for contract in contracts]))
    else:
        print('There is not any contract exists.')


@when('create', context='contract')
async def create_new_contract(dao: HolderDao, **_):
    print('Input the title:')
    title = input('... ')
    created: Contracts | None = await dao.contract.add_contract({'title': title})
    if created:
        print(f'Contract \"{created.title}\" has been created on {created.created_date}.')
    else:
        print('Sorry, some error has occurred.')


@when('confirm', context='contract')
@when('complete', context='contract')
async def change_contract_status(dao: HolderDao, cmd: str, **_):
    current_status = get_current_status(cmd=cmd)
    new_status = get_new_status(cmd=cmd)
    contracts_list: list[Contracts] = await choose_contract(dao=dao, status=current_status)
    if contracts_list:
        print(f'Available contracts:')
        show_contracts(contracts_list=contracts_list)

        print(f'Input the ID {cmd} the contract:')
        id_ = int(input('... '))
        await change_status_service(id_=id_,
                                    dao=dao,
                                    contracts_list=contracts_list,
                                    cmd=cmd,
                                    new_status=new_status)
    else:
        print(f'No available contracts to make the status \"{cmd}\".')


@when('back', context='contract')
async def back(**_):
    context = None
    set_context(context)


def show_contracts(contracts_list: list):
    index = [i for i in range(1, len(contracts_list) + 1)]
    data = [contract.to_df() for contract in contracts_list]
    df = DataFrame(data, index=index).to_markdown()
    print(df)
    print()


async def change_status_service(id_: int, dao: HolderDao, contracts_list: list, cmd: str, new_status: str):
    contract_to_change: Contracts | None = await dao.contract.get_contract_by_id(id_=id_)
    if contract_to_change and contract_to_change in contracts_list:
        status_changed = await change_status(dao=dao, cmd=cmd, contract_id=contract_to_change.id_)
        if status_changed:
            print(f'The status of \"{contract_to_change.title}\" '
                  f'has been changed to {new_status}.')
    else:
        print(f'There is no such contract to change the status to {new_status}.')


def get_current_status(cmd: str):
    return 'draft' if cmd == 'confirm' else 'active'


def get_new_status(cmd: str):
    return 'active' if cmd == 'confirm' else 'completed'


async def change_status(dao: HolderDao, cmd: str, contract_id: int) -> bool:
    hub = {
        'confirm': confirm_contract,
        'complete': complete_contract,
    }
    func = hub[cmd]
    status_changed = await func(dao=dao, contract_id=contract_id)
    return status_changed


async def choose_contract(dao: HolderDao, status: str):
    contracts_list = await dao.contract.get_contracts_with_status(status=status)
    return contracts_list


async def confirm_contract(dao: HolderDao, contract_id: int) -> bool:
    confirmed: bool = await dao.contract.sign_contract(new_status='active', id_=contract_id)
    return True if confirmed else False


async def complete_contract(dao: HolderDao, contract_id: int) -> bool:
    completed: bool = await dao.contract.update_status(id_=contract_id, new_status='completed')
    return True if completed else False
