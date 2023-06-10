from typing import Annotated, Optional

from pydantic import AnyHttpUrl, BaseModel, Field

from caller.enums import Method


class APICallBase(BaseModel):
    name: Optional[str] = None
    url: Annotated[Optional[str], AnyHttpUrl] = None
    method: Annotated[Optional[Method], Field()] = None
    content: Optional[str] = None
    # headers: Optional[dict] = Field(default=None)


class APICallCreate(APICallBase):
    name: str


class APICallUpdate(APICallBase):
    ...


class APICallGet(APICallBase):
    id: int
    name: str

    class Config:
        orm_mode = True


class APICallReady(APICallBase):
    id: int
    url: AnyHttpUrl
    method: Method

    class Config:
        orm_mode = True
