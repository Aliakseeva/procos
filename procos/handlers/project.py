"""
Handlers of commands related to the project system.
"""
from procos.cli import set_context, when
from procos.services.project import ProjectSystem


@when("project", context=None)
async def project_menu(**_):
    """show project menu."""
    context = "project"
    set_context(context)


@when("list", context="project")
async def list_all_projects(projects: ProjectSystem, **_):
    """list all projects."""
    await projects.list_all()


@when("create", context="project")
async def create_new_project(projects: ProjectSystem, **_):
    """create a new project."""
    await projects.create()


@when("attach", context="project")
async def attach_contract_to_project(projects: ProjectSystem, **_):
    """attach a contract to the project."""
    await projects.attach_contract()


@when("check", context="project")
async def check_contract_in_project(projects: ProjectSystem, **_):
    """check the contract in the project as completed."""
    await projects.check_contract()


@when("back", context="project")
async def back(**_):
    """get back to the main menu."""
    context = None
    set_context(context)
