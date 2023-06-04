from caller.crud.base import CRUDBase
from caller.db import APICall
from caller.schemas.api_calls import APICallCreate, APICallUpdate


class CRUDAPICall(CRUDBase[APICall, APICallCreate, APICallUpdate]):
    ...


api_call_crud = CRUDAPICall(APICall)
