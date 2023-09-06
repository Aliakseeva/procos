"""
Handlers of commands related to the contract system.
"""
from procos.cli import when, set_context
from procos.services.contract import ContractSystem


@when('contract', context=None)
async def contract_menu(**_):
    """show contract menu."""
    context = 'contract'
    set_context(context)


@when('list', context='contract')
async def list_all_contracts(contracts: ContractSystem, **_):
    """list all contracts."""
    await contracts.list_all()


@when('create', context='contract')
async def create_new_contract(contracts: ContractSystem, **_):
    """create a new contract."""
    await contracts.create()


@when('confirm', context='contract')
@when('complete', context='contract')
async def change_contract_status(contracts: ContractSystem, cmd: str, **_):
    """switch contract status."""
    await contracts.change_contract_status(cmd=cmd)


@when('back', context='contract')
async def back(**_):
    """get back to the main menu."""
    context = None
    set_context(context)
