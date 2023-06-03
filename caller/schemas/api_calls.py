from typing import Annotated, Optional

from pydantic import AnyUrl, BaseModel, Field


class APICallBase(BaseModel):
    name: Annotated[Optional[str], Field()] = None
    url: Annotated[Optional[str], AnyUrl] = None
    # headers: Optional[dict] = Field(default=None)


class APICallCreate(APICallBase):
    name: str


class APICallUpdate(APICallBase):
    ...


class APICallGet(APICallBase):
    id: int

    class Config:
        orm_mode = True
