from __future__ import annotations

from datetime import datetime, timezone

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from textual import on
from textual.app import App
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Label

from caller.crud import api_call_crud, header_crud, response_crud
from caller.db import Base
from caller.schemas.api_calls import APICallReady
from caller.schemas.responses import ResponseCreate
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
        api_call_list = self.query_one("#api-calls", ListViewVim)
        if api_call_list.index is None:
            return

        # highlight now api call
        api_call_list.index = len(api_call_list._nodes) - 1

    @on(APICallListScreen.Delete)
    def delete_api_call(self, event: APICallListScreen.Delete) -> None:
        api_call_crud.remove(self.session, obj=event.api_call)
        self.app.query_one(
            f"#api-call-list-item-{event.api_call.id}", APICallListItem
        ).remove()

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

        # TODO: Proper update method to update all individual static elements
        for key, value in event.obj_in.dict(exclude_unset=True).items():
            setattr(api_call_list_item, key, value)

    @on(APICallListScreen.CallAPI)
    def call_api(self, event: APICallListScreen.CallAPI) -> None:
        headers = {h.key: h.value for h in event.api_call.headers}
        params = {p.key: p.value for p in event.api_call.parameters}

        for g_header in header_crud.get_globals(self.session):
            headers[g_header.key] = g_header.value

        validated_call = APICallReady.from_orm(event.api_call)

        try:
            res = httpx.request(
                validated_call.method.value,
                validated_call.url,
                headers=headers,
                params=params,
                content=validated_call.content,
            )
        except httpx.HTTPError as e:
            self.query_one("#api-response-container", Container).mount(Label(str(e)))
            return

        resp_db = response_crud.create(
            self.session,
            obj_in=ResponseCreate(
                timestamp=datetime.now(timezone.utc),
                url=validated_call.url,
                code=res.status_code,
                method=validated_call.method,
                content=res.content,
                api_call_id=validated_call.id,
            ),
        )
        # TODO: Static reactive response widget
        self.query_one("#api-response-container", Container).mount(
            Label(str(res.json()))
        )


def run_tui_app(session: Session) -> None:
    app = MainApp(session, watch_css=True)
    app.run()


if __name__ == "__main__":
    engine = create_engine("sqlite:///api_call.db")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        run_tui_app(session)
