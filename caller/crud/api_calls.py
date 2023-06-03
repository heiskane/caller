from caller.crud.base import CRUDBase
from caller.db import APICallDB
from caller.schemas.api_calls import APICallCreate, APICallUpdate


class CRUDAPICalls(CRUDBase[APICallDB, APICallCreate, APICallUpdate]):
    ...


api_call_crud = CRUDAPICalls(APICallDB)
