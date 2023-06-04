from typing import Optional

from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from caller.enums import Methods


class Base(DeclarativeBase):
    pass


class APICallDB(Base):
    __tablename__ = "api_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    url: Mapped[Optional[str]]
    method: Mapped[Optional[Methods]]


class ResponseDB(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[Optional[str]]
    # TODO: Relations?
