from typing import Annotated, Optional

from pydantic import AnyUrl, BaseModel, Field

from caller.enums import Method


class APICallBase(BaseModel):
    name: Annotated[Optional[str], Field()] = None
    url: Annotated[Optional[str], AnyUrl] = None
    method: Annotated[Optional[Method], Field()] = None
    # headers: Optional[dict] = Field(default=None)


class APICallCreate(APICallBase):
    name: str


class APICallUpdate(APICallBase):
    ...


class APICallGet(APICallBase):
    id: int

    class Config:
        orm_mode = True


class APICallReady(APICallBase):
    id: int
    url: AnyUrl
    method: Method

    class Config:
        orm_mode = True
