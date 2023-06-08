from typing import Optional

from pydantic import BaseModel


class HeaderBase(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    api_call_id: Optional[int] = None


class HeaderCreate(HeaderBase):
    key: str
    value: str


class HeaderUpdate(HeaderBase):
    ...


class HeaderGet(HeaderBase):
    id: int

    class Config:
        orm_mode = True
