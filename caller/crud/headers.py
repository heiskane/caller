from sqlalchemy import select
from sqlalchemy.orm import Session

from caller.crud.base import CRUDBase
from caller.db import Header
from caller.schemas.headers import HeaderCreate, HeaderUpdate


class CRUDHeader(CRUDBase[Header, HeaderCreate, HeaderUpdate]):
    def get_globals(self, session: Session) -> list[Header]:
        stmt = select(Header).where(Header.api_call_id.is_(None))
        return list(session.execute(stmt).scalars())


header_crud = CRUDHeader(Header)
