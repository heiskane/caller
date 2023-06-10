from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from textual import on
from textual.app import App
from textual.binding import Binding
from textual.widgets import Label

from caller.crud import api_call_crud
from caller.db import Base
from caller.tui.screens import APICallListScreen, APICallViewScreen
from caller.tui.widgets import APICallListItem, APICallView, ListViewVim


class MainApp(App):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    session: Session

    def __init__(self, session: Session):
        super().__init__()
        self.session = session

    def on_mount(self) -> None:
        api_calls = api_call_crud.get_multi(self.session)
        self.push_screen(APICallListScreen(api_calls))

    def action_quit(self) -> None:
        self.exit()

    @on(APICallListScreen.Create)
    def create_api_call(self, event: APICallListScreen.Create) -> None:
        db_api_call = api_call_crud.create(self.session, obj_in=event.api_call)
        self.query_one("#api-calls", ListViewVim).append(APICallListItem(db_api_call))

    @on(APICallViewScreen.Update)
    def update_api_call(self, event: APICallViewScreen.Update) -> None:
        api_call = api_call_crud.update(
            self.session, db_obj=event.db_obj, obj_in=event.obj_in
        )
        self.query_one("#api-call-container", APICallView).api_call = api_call


def run_tui_app(session: Session) -> None:
    app = MainApp(session)
    app.run()


if __name__ == "__main__":
    engine = create_engine("sqlite:///api_call.db")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        run_tui_app(session)
