from sqlalchemy import select
from sqlalchemy.orm import Session

from caller.crud.base import CRUDBase
from caller.db import APICall, Response
from caller.schemas.responses import ResponseCreate, ResponseUpdate


class CRUDResponse(CRUDBase[Response, ResponseCreate, ResponseUpdate]):
    def get_by_api_call(self, session: Session, *, api_call: APICall) -> list[Response]:
        stmt = select(Response).where(Response.api_call == api_call)
        result = session.execute(stmt)
        return list(result.scalars())


response_crud = CRUDResponse(Response)
