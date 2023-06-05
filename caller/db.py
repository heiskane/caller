from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from caller.enums import Method


class Base(DeclarativeBase):
    pass


class APICall(Base):
    __tablename__ = "api_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    url: Mapped[Optional[str]]
    method: Mapped[Optional[Method]] = mapped_column(Enum(Method), default=Method.GET)
    content: Mapped[Optional[str]]

    responses: Mapped[list["Response"]] = relationship(back_populates="api_call")
    headers: Mapped[list["Header"]] = relationship(back_populates="api_call")
    parameters: Mapped[list["Parameter"]] = relationship(back_populates="api_call")


class Header(Base):
    __tablename__ = "headers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str]
    value: Mapped[str]

    api_call_id: Mapped[int] = mapped_column(ForeignKey("api_calls.id"))
    api_call: Mapped[APICall] = relationship(back_populates="headers")


class Parameter(Base):
    __tablename__ = "parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str]
    value: Mapped[str]

    api_call_id: Mapped[int] = mapped_column(ForeignKey("api_calls.id"))
    api_call: Mapped[APICall] = relationship(back_populates="parameters")


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    code: Mapped[int]
    content: Mapped[Optional[str]]
    url: Mapped[str]
    method: Mapped[Method]

    # TODO: req headers
    # TODO: resp header

    api_call_id: Mapped[int] = mapped_column(ForeignKey("api_calls.id"))
    api_call: Mapped[APICall] = relationship(back_populates="responses")
    # TODO: Relations?
