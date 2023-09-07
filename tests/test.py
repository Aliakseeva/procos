import io

import pytest

from procos.database.models import Contracts
from procos.services.contract import ContractSystem
from procos.services.project import ProjectSystem


@pytest.mark.asyncio
async def test_contract(test_contract: ContractSystem, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("Test Contract\n", newline="\n"))
    contract = await test_contract.create()

    assert contract, "Contract was not created."
    assert contract.status == "draft", "Default status is not DRAFT."

    monkeypatch.setattr("sys.stdin", io.StringIO(f"{contract.id_}\n", newline="\n"))
    confirmation = await test_contract.change_contract_status("confirm")
    assert confirmation, "Contract was not confirmed."
    assert contract.signed_date, "Contract sign date was not set."

    monkeypatch.setattr("sys.stdin", io.StringIO(f"{contract.id_}\n", newline="\n"))
    confirmation = await test_contract.change_contract_status("complete")
    assert confirmation, "Contract was not completed."


@pytest.mark.asyncio
async def test_project(test_project: ProjectSystem, test_contract: ContractSystem, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("Shouldn't be here\n", newline="\n"))
    created = await test_project.create()
    assert not created, "Must be forbidden to create new project w/o free and active contract."

    monkeypatch.setattr("sys.stdin", io.StringIO("Test Contract\n", newline="\n"))
    contract = await test_contract.create()
    monkeypatch.setattr("sys.stdin", io.StringIO(f"{contract.id_}\n", newline="\n"))
    await test_contract.change_contract_status("confirm")

    monkeypatch.setattr("sys.stdin", io.StringIO("Test Project\n", newline="\n"))
    project = await test_project.create()
    assert project, "Project was not created."

    monkeypatch.setattr(
        "sys.stdin", io.StringIO(f"{project.id_}\n" f"{contract.id_}", newline="\n")
    )
    attached = await test_project.attach_contract()
    assert attached, "Contract was now attached to the project."

    monkeypatch.setattr(
        "sys.stdin", io.StringIO(f"{project.id_}\n" f"{contract.id_}", newline="\n")
    )
    attached_again = await test_project.attach_contract()
    assert not attached_again, "Contract was attached twice."

    contracts: list[Contracts] = await test_contract.list_all()
    assert contracts[0].project_id_ == project.id_, "Contract project was not set."
