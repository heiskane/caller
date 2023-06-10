from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Label, ListItem, ListView

from caller.schemas.api_calls import APICallGet


class APICallListItem(ListItem):
    def __init__(self, api_call: APICallGet) -> None:
        super().__init__()
        self.api_call = api_call

    def compose(self) -> ComposeResult:
        yield Label(self.api_call.name)


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
