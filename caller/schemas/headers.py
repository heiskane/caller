from typing import Optional

from pydantic import BaseModel


class HeaderBase(BaseModel):
    key: Optional[str]
    value: Optional[str]
    api_call_id: Optional[int]


class HeaderCreate(HeaderBase):
    key: str
    value: str
    api_call_id: int


class HeaderUpdate(HeaderBase):
    ...


class HeaderGet(HeaderBase):
    id: int

    class Config:
        orm_mode = True
