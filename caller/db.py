from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from caller.enums import Method


class Base(DeclarativeBase):
    pass


class APICall(Base):
    __tablename__ = "api_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    url: Mapped[Optional[str]]
    method: Mapped[Optional[Method]]
    content: Mapped[Optional[str]]

    responses: Mapped[list["Response"]] = relationship(back_populates="api_call")


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
