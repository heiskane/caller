from __future__ import annotations

from rich.json import JSON
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, ListItem

from caller.crud import api_call_crud
from caller.schemas.api_calls import APICallCreate, APICallGet
from caller.tui.widgets import APICallListItem, ListViewVim


class CreateAPICall(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(id="api-call-name", placeholder="Name")
        yield Footer()

    @on(Input.Submitted, "#api-call-name")
    def create_api_call(self, event: Input.Submitted) -> None:
        api_call = api_call_crud.create(
            self.app.session, obj_in=APICallCreate(name=event.value)
        )

        # pop screen before query because otherwise
        # it seems to only find widgets on the create screen
        # and wont find the list of api calls
        self.app.pop_screen()
        self.app.query_one("#api-calls", ListViewVim).append(
            APICallListItem(APICallGet.from_orm(api_call))
        )


class APICallScreen(Screen):
    BINDINGS = [Binding("b", "exit", "exit")]

    def __init__(self, api_call: APICallGet) -> None:
        super().__init__()
        self.api_call = api_call

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(JSON(str(self.api_call.json())))
        yield Footer()

    def action_exit(self) -> None:
        self.app.pop_screen()


class APICallListScreen(Screen):
    BINDINGS = [
        Binding("c", "create_api_call", "Add API call"),
    ]
    api_calls = reactive([ListItem()])

    def compose(self) -> ComposeResult:
        self.api_calls = [
            APICallListItem(APICallGet.from_orm(i))
            for i in api_call_crud.get_multi(self.app.session)
        ]

        yield Header()
        yield ListViewVim(id="api-calls", *self.api_calls)
        yield Footer()

    def action_create_api_call(self) -> None:
        self.app.push_screen(CreateAPICall())

    @on(ListViewVim.Selected, "#api-calls")
    def open_api_call(self, event: ListViewVim.Selected) -> None:
        print(event.item.api_call)
        self.app.push_screen(APICallScreen(event.item.api_call))
