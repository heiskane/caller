import typer

from caller.main import init


def run_app() -> None:
    typer.run(init)
