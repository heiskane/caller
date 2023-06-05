from caller.crud.base import CRUDBase
from caller.db import Header
from caller.schemas.headers import HeaderCreate, HeaderUpdate


class CRUDHeader(CRUDBase[Header, HeaderCreate, HeaderUpdate]):
    ...


header_crud = CRUDHeader(Header)
