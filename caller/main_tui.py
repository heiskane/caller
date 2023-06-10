from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from textual.app import App
from textual.binding import Binding

from caller.db import Base
from caller.tui.screens import APICallListScreen


class MainApp(App):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    session: Session

    def on_mount(self) -> None:
        self.push_screen(APICallListScreen())

    def action_quit(self) -> None:
        self.exit()


def run_tui_app(session: Session) -> None:
    app = MainApp()
    app.session = session
    app.run()


if __name__ == "__main__":
    engine = create_engine("sqlite:///api_call.db")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        run_tui_app(session)
