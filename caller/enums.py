from enum import Enum, auto


class StrEnum(str, Enum):
    """
    StrEnum subclasses that create variants using
    `auto()` will have values equal to their names
    Enums inheriting from this class that set values
    using `enum.auto()` will have variant values equal to their names
    """

    # noinspection PyMethodParameters
    def _generate_next_value_(  # type: ignore
        name,
        start,
        count,
        last_values,
    ) -> str:
        """
        Uses the name as the automatic value, rather than an integer

        See https://docs.python.org/3/library/enum.html#using-automatic-values
        for reference
        """
        return name


class StrEnumLower(str, Enum):
    """
    StrEnum subclasses that create variants using
    `auto()` will have values equal to their names
    Enums inheriting from this class that set values
    using `enum.auto()` will have variant values
    equal to their lowercase names
    """

    # noinspection PyMethodParameters
    def _generate_next_value_(  # type: ignore
        name,
        start,
        count,
        last_values,
    ) -> str:
        """
        Uses the name as the automatic value, rather than an integer

        See https://docs.python.org/3/library/enum.html#using-automatic-values
        for reference
        """
        return name.lower()


class Method(StrEnum):
    GET = auto()
    POST = auto()
    PATCH = auto()
    PUT = auto()
    DELETE = auto()
    OPTIONS = auto()
