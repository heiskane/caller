from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.validation import ValidationResult
from textual.widgets import Input, Label, ListItem, ListView

from caller.db import APICall
from caller.enums import Method


class APICallsMainContainer(Container):
    def __init__(self, api_calls: list[APICall], id: str | None = None) -> None:
        super().__init__(id=id)
        self.api_calls = api_calls

    def compose(self) -> ComposeResult:
        yield Container(
            ListViewVim(
                id="api-calls",
                *[APICallListItem(i) for i in self.api_calls],
            ),
            id="api-calls-container",
        )
        yield APICallView(self.api_calls[0], id="api-call-details-side")


class APICallListItem(ListItem):
    api_call_name = reactive("default")
    api_call_method = reactive(Method.GET.value)
    api_call_url = reactive("default")

    def __init__(self, api_call: APICall) -> None:
        super().__init__(id=f"api-call-list-item-{api_call.id}")
        self.api_call = api_call
        self.api_call_name = api_call.name
        self.api_call_method = api_call.method.value
        self.api_call_url = api_call.url

    def render(self) -> str:
        return f"{self.name} - {self.api_call_method} - {self.api_call_url}"


class ListViewVim(ListView):
    BINDINGS = [
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
    ]

    class Selected(Message, bubble=True):
        def __init__(self, list_view: ListViewVim, item: APICallListItem) -> None:
            super().__init__()
            self.list_view: ListViewVim = list_view
            self.item: APICallListItem = item

        @property
        def control(self) -> ListViewVim:
            return self.list_view

    class Highlighted(Message, bubble=True):
        def __init__(
            self, list_view: ListViewVim, item: APICallListItem | None
        ) -> None:
            super().__init__()
            self.list_view: ListViewVim = list_view
            self.item: APICallListItem | None = item

        @property
        def control(self) -> ListViewVim:
            return self.list_view


class APICallView(Container):
    def __init__(self, api_call: APICall, id: str | None = None) -> None:
        super().__init__(id=id)
        self.api_call = api_call

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"name: {self.api_call.name}", id="selected-api-call-name"),
            Label(f"url: {str(self.api_call.url)}", id="selected-api-call-url"),
            Label(
                f"method: {self.api_call.method.value}", id="selected-api-call-method"
            ),
            Label("", id="api-call-response"),
        )

    # TODO: Do this reactively?
    def update_values(self) -> None:
        self.query_one("#selected-api-call-name", Label).update(
            f"name: {self.api_call.name}"
        )
        self.query_one("#selected-api-call-url", Label).update(
            f"url: {str(self.api_call.url)}"
        )


class ModifyAPICallInput(Input):
    def __init__(
        self,
        attribute: str,
        value: str | None = None,
        placeholder: str = "",
        id: str | None = None,
    ) -> None:
        super().__init__(
            value=value,
            placeholder=placeholder,
            id=id,
        )
        self.attribute = attribute

    @dataclass
    class Submitted(Message, bubble=True):
        input: ModifyAPICallInput
        value: str
        validation_result: ValidationResult | None = None

        @property
        def control(self) -> Input:
            return self.input
