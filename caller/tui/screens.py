from __future__ import annotations

from rich.json import JSON
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label

from caller.db import APICall
from caller.schemas.api_calls import APICallCreate, APICallGet, APICallUpdate
from caller.tui.widgets import APICallListItem, ListViewVim


class APICallViewScreen(Screen):
    BINDINGS = [Binding("b", "exit", "exit"), Binding("1", "set_url", "set url")]

    def __init__(self, api_call: APICall) -> None:
        super().__init__()
        self.api_call = api_call

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label(JSON(str(APICallGet.from_orm(self.api_call).json()))),
            id="api-call-container",
        )
        yield Footer()

    class Update(Message):
        def __init__(self, db_obj: APICall, obj_in: APICallUpdate) -> None:
            super().__init__()
            self.obj_in = obj_in
            self.db_obj = db_obj

    @on(Input.Submitted, "#api-call-url")
    def set_url(self, event: Input.Submitted) -> None:
        event.stop()
        self.post_message(self.Update(self.api_call, APICallUpdate(url=event.value)))
        event.input.remove()

    def action_set_url(self) -> None:
        input_widget = Input(id="api-call-url", placeholder="url")
        self.query_one("#api-call-container").mount(input_widget)
        input_widget.focus()

    def action_exit(self) -> None:
        self.app.pop_screen()


class APICallListScreen(Screen):
    BINDINGS = [
        Binding("c", "create_api_call", "Add API call"),
    ]

    def __init__(self, api_calls: list[APICall]) -> None:
        super().__init__()
        self.api_calls = api_calls

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            ListViewVim(id="api-calls", *[APICallListItem(i) for i in self.api_calls]),
            id="api-calls-container",
        )
        yield Footer()

    class Create(Message):
        def __init__(self, api_call: APICallCreate) -> None:
            super().__init__()
            self.api_call = api_call

    def action_create_api_call(self) -> None:
        input_widget = Input(id="api-call-name", placeholder="Name")
        self.query_one("#api-calls-container").mount(input_widget)
        input_widget.focus()

    @on(ListViewVim.Selected, "#api-calls")
    def open_api_call(self, event: ListViewVim.Selected) -> None:
        self.app.push_screen(APICallViewScreen(event.item.api_call))

    @on(Input.Submitted, "#api-call-name")
    def create_api_call(self, event: Input.Submitted) -> None:
        # https://textual.textualize.io/guide/widgets/#__tabbed_1_1
        # not sure if nessesary but it is used in the documentation
        event.stop()
        self.post_message(self.Create(APICallCreate(name=event.value)))
        event.input.remove()
