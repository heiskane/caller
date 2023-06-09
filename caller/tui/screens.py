from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label

from caller.db import APICall
from caller.schemas.api_calls import APICallCreate, APICallUpdate
from caller.tui.widgets import (
    APICallsMainContainer,
    APICallView,
    ListViewVim,
    ModifyAPICallInput,
)


class APICallListScreen(Screen):
    BINDINGS = [
        Binding("c", "create_api_call", "Add API call"),
        Binding("g", "go_top", "Go to top"),
        Binding("G", "go_bottom", "Go to bottom"),
        Binding("s", "set_url", "Set url"),
        Binding("u", "set_method", "Set method"),
        Binding("t", "set_content", "Set content"),
        Binding("r", "rename", "Rename"),
        Binding("d", "delete_api_call", "Delete"),
    ]

    def __init__(self, api_calls: list[APICall]) -> None:
        super().__init__()
        self.api_calls = api_calls

    def compose(self) -> ComposeResult:
        yield Header()
        yield APICallsMainContainer(self.api_calls, id="api-calls-main-container")
        yield Footer()

    class Create(Message):
        def __init__(self, api_call: APICallCreate) -> None:
            super().__init__()
            self.api_call = api_call

    class Delete(Message):
        def __init__(self, api_call: APICall) -> None:
            super().__init__()
            self.api_call = api_call

    class Update(Message):
        def __init__(
            self, container: APICallView, db_obj: APICall, obj_in: APICallUpdate
        ) -> None:
            super().__init__()
            self.container = container
            self.obj_in = obj_in
            self.db_obj = db_obj

    class CallAPI(Message):
        def __init__(self, api_call: APICall) -> None:
            super().__init__()
            self.api_call = api_call

    def action_create_api_call(self) -> None:
        input_widget = Input(id="api-call-name", placeholder="Name")
        self.query_one("#api-call-details-side").mount(input_widget)
        input_widget.focus()

    def action_delete_api_call(self) -> None:
        api_call_list_item = self.query_one("#api-calls", ListViewVim).highlighted_child
        if api_call_list_item is None:
            return None

        self.post_message(self.Delete(api_call_list_item.api_call))

        api_call_list = self.query_one("#api-calls", ListViewVim)
        if api_call_list.index is None:
            return

        api_call_list.index -= 1

    def action_go_bottom(self) -> None:
        self.query_one("#api-calls", ListViewVim).index = len(self.api_calls) - 1

    def action_go_top(self) -> None:
        self.query_one("#api-calls", ListViewVim).index = 0

    def action_set_url(self) -> None:
        api_call_list_item = self.query_one("#api-calls", ListViewVim).highlighted_child
        if api_call_list_item is None:
            return None

        input_widget = ModifyAPICallInput(
            id="api-call-update",
            value=api_call_list_item.api_call.url,
            attribute="url",
            placeholder="url",
        )
        self.query_one("#api-call-details-side").mount(input_widget)
        input_widget.focus()

    def action_set_method(self) -> None:
        api_call_list_item = self.query_one("#api-calls", ListViewVim).highlighted_child
        if api_call_list_item is None:
            return None

        input_widget = ModifyAPICallInput(
            id="api-call-update",
            attribute="method",
            placeholder="method",
        )
        self.query_one("#api-call-details-side").mount(input_widget)
        input_widget.focus()

    def action_set_content(self) -> None:
        api_call_list_item = self.query_one("#api-calls", ListViewVim).highlighted_child
        if api_call_list_item is None:
            return None

        input_widget = ModifyAPICallInput(
            id="api-call-update",
            attribute="content",
            placeholder="content",
        )
        self.query_one("#api-call-details-side").mount(input_widget)
        input_widget.focus()

    def action_rename(self) -> None:
        api_call_list_item = self.query_one("#api-calls", ListViewVim).highlighted_child
        if api_call_list_item is None:
            return None

        input_widget = ModifyAPICallInput(
            id="api-call-update",
            attribute="name",
            placeholder="name",
        )
        self.query_one("#api-call-details-side").mount(input_widget)
        input_widget.focus()

    @on(ModifyAPICallInput.Submitted, "#api-call-update")
    def update_api_call(self, event: ModifyAPICallInput.Submitted) -> None:
        event.stop()

        api_call_list_item = self.query_one("#api-calls", ListViewVim).highlighted_child
        if api_call_list_item is None:
            return None

        api_call_update = APICallUpdate()
        setattr(api_call_update, event.input.attribute, event.value)

        api_call_view = self.query_one("#api-call-details-side", APICallView)
        self.post_message(
            self.Update(api_call_view, api_call_list_item.api_call, api_call_update)
        )
        event.input.remove()

    @on(ListViewVim.Highlighted)
    def display_api_call_info(self, event: ListViewVim.Highlighted) -> None:
        api_call_view = self.query_one("#api-call-details-side", APICallView)
        if event.item is None:
            return

        api_call_view.api_call = event.item.api_call
        api_call_view.update_values()

        if len(event.item.api_call.responses) > 0:
            self.query_one("#response-content", Label).update(
                str(event.item.api_call.responses[0].content)
            )

    @on(ListViewVim.Selected, "#api-calls")
    def call_api(self) -> None:
        api_call_list_item = self.query_one("#api-calls", ListViewVim).highlighted_child
        if api_call_list_item is None:
            return None

        self.post_message(self.CallAPI(api_call_list_item.api_call))

    @on(Input.Submitted, "#api-call-name")
    def create_api_call(self, event: Input.Submitted) -> None:
        # https://textual.textualize.io/guide/widgets/#__tabbed_1_1
        # not sure if nessesary but it is used in the documentation
        event.stop()
        self.post_message(self.Create(APICallCreate(name=event.value)))
        event.input.remove()
