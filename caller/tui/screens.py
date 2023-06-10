from __future__ import annotations

from rich.json import JSON
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, ListItem

from caller.crud import api_call_crud
from caller.schemas.api_calls import APICallCreate, APICallGet
from caller.tui.widgets import APICallListItem, ListViewVim


class APICallViewScreen(Screen):
    BINDINGS = [Binding("b", "exit", "exit")]

    def __init__(self, api_call: APICallGet) -> None:
        super().__init__()
        self.api_call = api_call

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(JSON(str(self.api_call.json())))
        yield Footer()

    def action_set_url(self) -> None:
        ...

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
        yield Container(
            ListViewVim(id="api-calls", *self.api_calls), id="main-container"
        )
        yield Footer()

    def action_create_api_call(self) -> None:
        input_widget = Input(id="api-call-name", placeholder="Name")
        self.query_one("#main-container").mount(input_widget)
        input_widget.focus()

    @on(ListViewVim.Selected, "#api-calls")
    def open_api_call(self, event: ListViewVim.Selected) -> None:
        print(event.item.api_call)
        self.app.push_screen(APICallViewScreen(event.item.api_call))

    @on(Input.Submitted, "#api-call-name")
    async def create_api_call(self, event: Input.Submitted) -> None:
        # https://textual.textualize.io/guide/widgets/#__tabbed_1_1
        # not sure if nessesary but it is used in the documentation
        event.stop()

        # TODO: do this with messages?
        api_call = api_call_crud.create(
            self.app.session, obj_in=APICallCreate(name=event.value)
        )
        self.api_calls.append(APICallListItem(APICallGet.from_orm(api_call)))
        self.query_one("#api-calls", ListViewVim).append(
            APICallListItem(APICallGet.from_orm(api_call))
        )
        event.input.remove()
