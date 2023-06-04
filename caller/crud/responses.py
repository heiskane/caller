from caller.crud.base import CRUDBase
from caller.db import Response
from caller.schemas.responses import ResponseCreate, ResponseUpdate


class CRUDResponse(CRUDBase[Response, ResponseCreate, ResponseUpdate]):
    ...


response_crud = CRUDResponse(Response)
