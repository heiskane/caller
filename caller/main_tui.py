from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView

from caller.crud.api_calls import api_call_crud
from caller.db import Base
from caller.schemas.api_calls import APICallCreate, APICallGet


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


class CreateAPICall(Screen):
    def compose(self) -> ComposeResult:
        yield Input(id="api-call-name", placeholder="Name")

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
    def compose(self) -> ComposeResult:
        return super().compose()


class MainApp(App):
    BINDINGS = [
        Binding("c", "create_api_call", "Add API call"),
        Binding("q", "quit", "Quit"),
    ]
    session: Session
    api_calls = reactive([ListItem()])

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        self.api_calls = [
            APICallListItem(APICallGet.from_orm(i))
            for i in api_call_crud.get_multi(self.session)
        ]

        yield ListViewVim(id="api-calls", *self.api_calls)
        yield Footer()

    def action_create_api_call(self) -> None:
        self.push_screen(CreateAPICall())

    def action_quit(self) -> None:
        self.exit()

    @on(ListViewVim.Selected, "#api-calls")
    def open_api_call(self, event: ListViewVim.Selected) -> None:
        print(event.item.api_call)
        self.push_screen(APICallScreen())


def run_tui_app(session: Session) -> None:
    app = MainApp()
    app.session = session
    app.run()


if __name__ == "__main__":
    engine = create_engine("sqlite:///api_call.db")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        run_tui_app(session)
