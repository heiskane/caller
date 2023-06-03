from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from caller.enums import Methods


class Base(DeclarativeBase):
    pass


class APICallDB(Base):
    __tablename__ = "api_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    url: Mapped[str] = mapped_column(String, nullable=True)
    method: Mapped[Methods]
