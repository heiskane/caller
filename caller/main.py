from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import auto
from typing import Callable, Optional

import httpx
import typer
from pydantic import AnyUrl, ValidationError
from rich import print
from rich.console import Console
from rich.json import JSON
from rich.prompt import Prompt
from sqlalchemy import Enum, create_engine
from sqlalchemy.orm import Session

from caller.crud.api_calls import api_call_crud
from caller.crud.responses import response_crud
from caller.db import APICall, Base
from caller.enums import Method
from caller.schemas.api_calls import (
    APICallCreate,
    APICallGet,
    APICallReady,
    APICallUpdate,
)
from caller.schemas.responses import ResponseCreate, ResponseGet


@dataclass
class AppMenu:
    console: Console
    err_console: Console
    session: Session
    running: bool = True
    options: list[tuple[Callable[[], None], str]] = field(default_factory=list)

    def run(self) -> None:
        while self.running:
            self._pre_run()
            self._display_options()

            choice = None
            while choice is None:
                choice_str = Prompt.ask("choice")
                choice = self._validate_menu_choice(choice_str)

            action, _ = self.options[choice - 1]
            action()

    def _pre_run(self) -> None:
        ...

    def _print_err(self, msg: str) -> None:
        self.err_console.print(f"[red]ERROR: [bold]{msg}")

    def _exit(self) -> None:
        self.running = False

    def _display_options(self) -> None:
        for num, opt in enumerate(self.options, start=1):
            print(f"{num}: [bold green]{opt[1]}[/bold green]")

    def _validate_menu_choice(self, choice_str: str) -> Optional[int]:
        if not choice_str.isdigit():
            # self._print_err("choice must be int")
            return None

        choice = int(choice_str)

        if choice < 1 or choice > len(self.options):
            self._print_err("invalid selection")
            return None

        return choice


class MainMenu(AppMenu):
    def __init__(
        self, session: Session, console: Console, err_console: Console
    ) -> None:
        self.session = session
        self.console = console
        self.err_console = err_console
        self.options = [
            (self._create_api_call, "create new api call"),
            (self._list_api_calls, "list api calls"),
            (self._open_api_call, "open api call"),
        ]

    def _open_main_menu(self) -> None:
        self.current_menu = Menu.MAIN

    def _create_api_call(self) -> None:
        name = Prompt.ask("name")
        create_obj = APICallCreate(name=name)
        api_call_crud.create(self.session, obj_in=create_obj)

    def _list_api_calls(self) -> None:
        # TODO: Pagination?
        api_calls = api_call_crud.get_multi(self.session)

        print()
        for api_call in api_calls:
            print(f"{api_call.id}: {APICallGet.from_orm(api_call)}")

        print()

    def _open_api_call(self) -> None:
        self._list_api_calls()
        api_call_id = Prompt.ask("provide api call id")

        if (api_call := api_call_crud.get(self.session, id=api_call_id)) is None:
            self._print_err("api call not found")
            return

        api_call_menu = APICallMenu(
            self.session, api_call, self.console, self.err_console
        )
        api_call_menu.run()


class APICallMenu(AppMenu):
    def __init__(
        self,
        session: Session,
        api_call: APICall,
        console: Console,
        err_console: Console,
    ) -> None:
        self.running = True
        self.selected_api_call = api_call
        self.session = session
        self.console = console
        self.err_console = err_console
        self.options = [
            (self._call_api, "call api"),
            (self._set_url, "set url"),
            (self._set_method, "set method"),
            (self._set_content, "set content"),
            (self._list_responses, "list responses"),
            (self._exit, "back"),
        ]

    def _pre_run(self) -> None:
        self.console.print(APICallGet.from_orm(self.selected_api_call))

    def _set_method(self) -> None:
        method_input = Prompt.ask("method", default=Method.GET.value)
        method = Method(method_input)
        api_call_crud.update(
            self.session,
            db_obj=self.selected_api_call,
            obj_in=APICallUpdate(method=method),
        )

    def _set_content(self) -> None:
        content = Prompt.ask("content")
        api_call_crud.update(
            self.session,
            db_obj=self.selected_api_call,
            obj_in=APICallUpdate(content=content),
        )

    def _list_responses(self) -> None:
        # TODO: Pagination?
        responses = response_crud.get_by_api_call(
            self.session, api_call=self.selected_api_call
        )

        print()
        for response in responses:
            print(f"{response.id}: {ResponseGet.from_orm(response)}")

        print()

    def _call_api(self) -> None:
        try:
            validated_call = APICallReady.from_orm(self.selected_api_call)
        except ValidationError as e:
            self._print_err("api call not ready to send")
            __import__("pprint").pprint(e.errors())
            return

        try:
            res = httpx.request(
                validated_call.method.value,
                validated_call.url,
                content=validated_call.content,
            )
        except httpx.RequestError:
            self._print_err("request error")
            return
        # except httpx.HTTPStatusError:
        #     self.err_console.print("request failed with error code", res.status_code)
        #
        #     if res.content:
        #         self.err_console.print(res.content)
        #
        #     return

        if res.is_success is False:
            ...

        print()
        print(res.json())
        print()

        self.console.print(JSON(res.content.decode()))
        response_crud.create(
            self.session,
            obj_in=ResponseCreate(
                timestamp=datetime.now(timezone.utc),
                url=validated_call.url,
                code=res.status_code,
                method=validated_call.method,
                # TODO: Maybe keep it in bytes?
                content=str(res.content),
                api_call_id=validated_call.id,
            ),
        )

    def _set_url(self) -> None:
        scheme = Prompt.ask("scheme", default="http")
        host = Prompt.ask("host", default="localhost")
        port = Prompt.ask("port", default="8000")
        path = Prompt.ask("path", default="/")

        url = AnyUrl.build(scheme=scheme, host=host, port=port, path=path)
        api_call_crud.update(
            self.session, db_obj=self.selected_api_call, obj_in=APICallUpdate(url=url)
        )


class Menu(Enum):
    MAIN = auto()
    API_CALL = auto()


def init(debug: bool = False):
    engine = create_engine("sqlite:///api_call.db", echo=debug)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        api_app = MainMenu(
            session=session,
            console=Console(),
            err_console=Console(stderr=True),
        )
        api_app.run()


if __name__ == "__main__":
    typer.run(init)
