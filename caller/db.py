from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Table
from sqlalchemy.dialects.sqlite import BLOB, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from caller.enums import Method


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class APICall(Base):
    __tablename__ = "api_calls"

    name: Mapped[str]
    url: Mapped[Optional[str]]
    method: Mapped[Optional[Method]] = mapped_column(Enum(Method), default=Method.GET)
    content: Mapped[Optional[str]]

    responses: Mapped[list["Response"]] = relationship(back_populates="api_call")
    headers: Mapped[list["Header"]] = relationship(back_populates="api_call")
    parameters: Mapped[list["Parameter"]] = relationship(back_populates="api_call")

    def __str__(self) -> str:
        # fmt: off
        return "\n".join([
            f"API_CALL={self.name}",
            f"url={self.url}",
            f"method={self.method}",
            f"content={self.content}",
        ])
        # fmt: on


req_headers = Table(
    "req_headers",
    Base.metadata,
    Column("header_id", ForeignKey("headers.id"), primary_key=True),
    Column("response_id", ForeignKey("responses.id"), primary_key=True),
)


class Header(Base):
    __tablename__ = "headers"

    key: Mapped[str]
    value: Mapped[str]

    api_call_id: Mapped[Optional[int]] = mapped_column(ForeignKey("api_calls.id"))
    api_call: Mapped[Optional[APICall]] = relationship(back_populates="headers")


class Parameter(Base):
    __tablename__ = "parameters"

    key: Mapped[str]
    value: Mapped[str]

    api_call_id: Mapped[int] = mapped_column(ForeignKey("api_calls.id"))
    api_call: Mapped[APICall] = relationship(back_populates="parameters")


class Response(Base):
    __tablename__ = "responses"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    code: Mapped[int]
    content: Mapped[Optional[bytes]]
    url: Mapped[str]
    method: Mapped[Method]

    data: Mapped[Optional[dict[str, dict[str, str]]]] = mapped_column(JSON)

    api_call_id: Mapped[int] = mapped_column(ForeignKey("api_calls.id"))
    api_call: Mapped[APICall] = relationship(back_populates="responses")

    def __str__(self) -> str:
        string = f"{self.timestamp}: id={self.id}, code={self.code}"
        if self.content is not None:
            trunc_content = (
                (self.content.decode()[:50] + "...")
                if len(self.content) > 75
                else self.content.decode()
            )
            string += f", content={trunc_content}"
        return string
