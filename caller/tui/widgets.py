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
    # TODO: better reactive stuff
    name = reactive("default")

    def __init__(self, api_call: APICall) -> None:
        super().__init__(id=f"api-call-list-item-{api_call.id}")
        self.api_call = api_call
        self.name = self.api_call.name

    def render(self) -> str:
        return f"{self.name}"


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

    @property
    def highlighted_child(self) -> APICallListItem | None:
        if self.index is not None and 0 <= self.index < len(self._nodes):
            list_item = self._nodes[self.index]
            assert isinstance(list_item, APICallListItem)
            return list_item
        else:
            return None


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
            Label(f"content: {self.api_call.content}", id="selected-api-call-content"),
            Label("", id="api-call-response"),
            id="api-call-side-container",
        )

    # TODO: Do this reactively?
    def update_values(self) -> None:
        self.query_one("#selected-api-call-name", Label).update(
            f"name: {self.api_call.name}"
        )
        self.query_one("#selected-api-call-url", Label).update(
            f"url: {str(self.api_call.url)}"
        )
        self.query_one("#selected-api-call-method", Label).update(
            f"method: {str(self.api_call.method.value)}"
        )
        self.query_one("#selected-api-call-content", Label).update(
            f"content: {self.api_call.content}"
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
