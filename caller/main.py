from typing import Optional

import httpx
import typer
from pydantic import AnyUrl, BaseModel, Field, ValidationError
from rich import print
from rich.console import Console
from rich.prompt import Prompt
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


class APICallGet(APICallBase):
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


def list_api_calls(session: Session):
    stmt = select(APICallDB)
    api_calls = session.execute(stmt).scalars()

    for api_call in api_calls:
        print(f"{api_call.id}: {APICallGet.from_orm(api_call)}")

    print("-------------------------------")


def modify_api_call(session: Session):
    api_call_id = Prompt.ask("provide api call id")

    stmt = select(APICallDB).where(APICallDB.id == api_call_id)
    api_call = session.execute(stmt).scalars().first()

    if api_call is None:
        err_console.print("api call not found")
        return

    print(APICallGet.from_orm(api_call))

    print("modify api call")

    stuff = {}
    for i, prop in enumerate(APICallUpdate.schema()["properties"].keys(), start=1):
        stuff[i] = prop
    print(stuff)

    prop_input = int(Prompt.ask("field to modify"))
    prop_value = Prompt.ask(f"value to field {stuff[prop_input]}")

    try:
        update_obj = APICallUpdate(**{stuff[prop_input]: prop_value})
    except ValidationError as e:
        for err in e.errors():
            err_console.print("validation failed", err["msg"])
        return

    update_data = update_obj.dict(exclude_unset=True)
    for field in update_data.keys():
        setattr(api_call, field, update_data[field])

    session.add(api_call)
    session.commit()
    session.refresh(api_call)


def open_api_call(session: Session) -> None:
    api_call_id = Prompt.ask("provide api call id")

    stmt = select(APICallDB).where(APICallDB.id == api_call_id)
    api_call = session.execute(stmt).scalars().first()

    if api_call is None:
        err_console.print("api call not found")
        return

    print(APICallGet.from_orm(api_call))

    action = int(Prompt.ask("action"))

    API_CALL_ACTIONS[action][0](api_call)


def call_api(api_call: APICallDB) -> None:
    res = httpx.get(api_call.url)
    print()
    print(res.json())
    print()


API_CALL_ACTIONS = {
    1: (call_api, "call api"),
}


COMMAND_OPTIONS = {
    1: (create_api_call, "create new api call"),
    2: (list_api_calls, "list api calls"),
    3: (open_api_call, "open api call"),
    4: (modify_api_call, "modify api call"),
}

console = Console()
err_console = Console(stderr=True)


def app(session: Session):
    # print(APICall.schema())
    # raise typer.Exit(code=0)
    # list_api_calls(session)

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
