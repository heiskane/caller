from caller.crud.base import CRUDBase
from caller.db import Parameter
from caller.schemas.parameters import ParameterCreate, ParameterUpdate


class CRUDParameter(CRUDBase[Parameter, ParameterCreate, ParameterUpdate]):
    ...


parameter_crud = CRUDParameter(Parameter)
