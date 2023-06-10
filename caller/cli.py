import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from caller.db import Base
from caller.main import init
from caller.main_tui import run_tui_app


def run_app() -> None:
    typer.run(init)


def run_tui() -> None:
    engine = create_engine("sqlite:///api_call.db")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        run_tui_app(session)
