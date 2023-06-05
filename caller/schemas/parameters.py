from typing import Optional

from pydantic import BaseModel


class ParameterBase(BaseModel):
    key: Optional[str]
    value: Optional[str]
    api_call_id: Optional[int]


class ParameterCreate(ParameterBase):
    key: str
    value: str
    api_call_id: int


class ParameterUpdate(ParameterBase):
    ...


class ParameterGet(ParameterBase):
    id: int

    class Config:
        orm_mode = True
