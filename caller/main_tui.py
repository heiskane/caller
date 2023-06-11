from __future__ import annotations

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from textual import on
from textual.app import App
from textual.binding import Binding
from textual.widgets import Label

from caller.crud import api_call_crud, header_crud
from caller.db import Base
from caller.schemas.api_calls import APICallReady
from caller.tui.screens import APICallListScreen
from caller.tui.widgets import APICallListItem, ListViewVim


class MainApp(App):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    CSS_PATH = "style/style.css"

    def __init__(self, session: Session, watch_css: bool = False):
        super().__init__(watch_css=watch_css)
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

    @on(APICallListScreen.Update)
    def update_api_call(self, event: APICallListScreen.Update) -> None:
        print("UPDATING:", event.obj_in)
        api_call = api_call_crud.update(
            self.session, db_obj=event.db_obj, obj_in=event.obj_in
        )
        event.container.api_call = api_call
        event.container.update_values()

        api_call_list_item = self.app.query_one(
            f"#api-call-list-item-{api_call.id}", APICallListItem
        )
        for key, value in event.obj_in.dict(exclude_unset=True).items():
            setattr(api_call_list_item, key, value)

    @on(APICallListScreen.CallAPI)
    def call_api(self, event: APICallListScreen.CallAPI) -> None:
        headers = {h.key: h.value for h in event.api_call.headers}
        params = {p.key: p.value for p in event.api_call.parameters}

        for g_header in header_crud.get_globals(self.session):
            headers[g_header.key] = g_header.value

        validated_call = APICallReady.from_orm(event.api_call)

        res = httpx.request(
            validated_call.method.value,
            validated_call.url,
            headers=headers,
            params=params,
            content=validated_call.content,
        )

        self.query_one("#api-call-response", Label).update(str(res.content))


def run_tui_app(session: Session) -> None:
    app = MainApp(session, watch_css=True)
    app.run()


if __name__ == "__main__":
    engine = create_engine("sqlite:///api_call.db")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        run_tui_app(session)
