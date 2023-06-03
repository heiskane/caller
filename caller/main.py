from typing import Callable

import httpx
import typer
from pydantic import AnyUrl
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from caller.crud.api_calls import api_call_crud
from caller.db import APICallDB, Base
from caller.schemas.api_calls import APICallCreate, APICallGet, APICallUpdate


def create_api_call(session: Session) -> None:
    name = Prompt.ask("name")
    create_obj = APICallCreate(name=name)
    api_call_crud.create(session, obj_in=create_obj)


def list_api_calls(session: Session):
    # TODO: Pagination?
    api_calls = api_call_crud.get_multi(session)

    for api_call in api_calls:
        print(f"{api_call.id}: {APICallGet.from_orm(api_call)}")

    print("-------------------------------")


# TODO: Wrapper around this?
def open_api_call(session: Session) -> None:
    api_call_id = Prompt.ask("provide api call id")

    api_call = api_call_crud.get(session, id=api_call_id)

    if api_call is None:
        err_console.print("api call not found")
        return

    while True:
        print(APICallGet.from_orm(api_call))

        for num, option in API_CALL_ACTIONS.items():
            print(f"{num}: [bold green]{option[1]}[/bold green]")

        action = int(Prompt.ask("action"))

        # TODO: this aint it chief
        if action == 9:
            break

        API_CALL_ACTIONS[action][0](session, api_call)


def call_api(_session: Session, api_call: APICallDB) -> None:
    res = httpx.get(api_call.url)

    try:
        res.raise_for_status()
    except httpx.HTTPStatusError:
        err_console.print("request failed with error code", res.status_code)

        if res.content:
            err_console.print(res.content)

        return

    print()
    print(res.json())
    print()


def set_url(session: Session, api_call: APICallDB) -> None:
    # TODO: Defaults
    scheme = Prompt.ask("scheme")
    host = Prompt.ask("host")
    port = Prompt.ask("port")
    path = Prompt.ask("path")

    url = AnyUrl.build(scheme=scheme, host=host, port=port, path=path)

    api_call_crud.update(session, db_obj=api_call, obj_in=APICallUpdate(url=url))


API_CALL_ACTIONS: dict[int, tuple[Callable[[Session, APICallDB], None], str]] = {
    1: (call_api, "call api"),
    2: (set_url, "set url"),
    # TODO: Add param
    # TODO: Add header
    # TODO: Add json data creation thingy?
}


COMMAND_OPTIONS: dict[int, tuple[Callable[[Session], None], str]] = {
    1: (create_api_call, "create new api call"),
    2: (list_api_calls, "list api calls"),
    3: (open_api_call, "open api call"),
}

console = Console()
err_console = Console(stderr=True)


def app(session: Session):
    for num, option in COMMAND_OPTIONS.items():
        print(f"{num}: [bold green]{option[1]}[/bold green]")

    choise = int(Prompt.ask("choise"))

    action, _ = COMMAND_OPTIONS[choise]

    typer.clear()
    action(session)
    # COMMAND_OPTIONS[choise][0](session)


def init(debug: bool = False):
    engine = create_engine("sqlite://", echo=debug)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        while True:
            app(session)


if __name__ == "__main__":
    typer.run(init)
