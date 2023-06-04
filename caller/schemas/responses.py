from datetime import datetime
from typing import Annotated, Optional

from pydantic import AnyUrl, BaseModel, Field

from caller.enums import Method


class ResponseBase(BaseModel):
    code: Optional[int]
    content: Annotated[Optional[str], Field()]
    url: Annotated[Optional[str], AnyUrl]
    method: Annotated[Optional[Method], Field()] = None
    api_call_id: Optional[int]


class ResponseCreate(ResponseBase):
    timestamp: datetime
    code: int
    url: Annotated[str, AnyUrl]
    method: Method
    api_call_id: int


class ResponseUpdate(ResponseBase):
    ...


class ResponseGet(ResponseBase):
    timestamp: datetime
    id: int

    class Config:
        orm_mode = True
