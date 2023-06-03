from typing import Optional

import httpx
import typer
from pydantic import AnyUrl, BaseModel, Field, ValidationError
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class APICallDB(Base):
    __tablename__ = "api_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    url: Mapped[str] = mapped_column(String, nullable=True)


class APICallBase(BaseModel):
    name: Optional[str] = Field(default=None)
    url: Optional[AnyUrl] = Field(default=None)
    # headers: Optional[dict] = Field(default=None)


class APICallCreate(APICallBase):
    name: str


class APICallUpdate(APICallBase):
    ...


class APICallGet(BaseModel):
    id: int

    class Config:
        orm_mode = True


def create_api_call(session: Session):
    name = Prompt.ask("name")
    create_obj = APICallCreate(name=name)
    db_obj = APICallDB(**create_obj.dict(exclude_unset=True))
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    modify_api_call(db_obj.id, session)


def list_api_calls(session: Session):
    stmt = select(APICallDB)
    api_calls = session.execute(stmt).scalars()

    # TODO: Use model schema to dynamically do things
    table = Table("id", "name", "url")

    for api_call in api_calls:
        table.add_row(
            str(api_call.id),
            api_call.name,
            api_call.url,
        )
    console.print(table)


def modify_api_call(id: int, session: Session):
    stmt = select(APICallDB).where(APICallDB.id == id)
    api_call = session.execute(stmt).scalars().first()
    # print(api_call.__dict__)

    if api_call is None:
        print("api call not found")
        return

    print("modify api call")

    stuff = {}
    for i, prop in enumerate(APICallUpdate.schema()["properties"].keys(), start=1):
        stuff[i] = prop
        # print(prop, getattr(api_call, prop))
    print(stuff)

    prop_input = int(Prompt.ask("field to modify"))
    prop_value = Prompt.ask(f"value to field {stuff[prop_input]}")

    try:
        update_obj = APICallUpdate(**{stuff[prop_input]: prop_value})
    except ValidationError as e:
        for err in e.errors():
            err_console.print("validation failed", err["msg"])
        modify_api_call(id, session)
    # setattr(update_obj, stuff[prop_input], prop_value)

    update_data = update_obj.dict(exclude_unset=True)
    for field in update_data.keys():
        setattr(api_call, field, update_data[field])

    session.add(api_call)
    session.commit()
    # session.refresh(api_call)

    modify_api_call(id, session)


COMMAND_OPTIONS = {
    1: (create_api_call, "create new api call"),
}

console = Console()
err_console = Console(stderr=True)


def app(session: Session):
    # print(APICall.schema())
    # raise typer.Exit(code=0)
    list_api_calls(session)

    for num, option in COMMAND_OPTIONS.items():
        print(f"{num}: [bold green]{option[1]}[/bold green]")

    choise = int(Prompt.ask("choise"))

    COMMAND_OPTIONS[choise][0](session)


def init(debug: bool = False):
    engine = create_engine("sqlite://", echo=debug)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        while True:
            app(session)


if __name__ == "__main__":
    typer.run(init)
