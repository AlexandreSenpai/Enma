from dataclasses import asdict
import dataclasses
from datetime import datetime, timezone
from enum import Enum
import json
from typing import Callable, Generic, Literal, TypeVar, Union, cast
from uuid import uuid4

T = TypeVar("T")
PROCESSORS = Union[
    Literal["from_dataclass"],
    Literal["from_entity"],
    Literal["from_dict"],
    Literal["from_list"],
    Literal["from_datetime"],
    Literal["from_enum"],
]


class Entity(Generic[T]):
    """Base class for entities in the domain model.

    This class provides common attributes and methods for all entities.

    Attributes:
        id: A Union of int and str representing the entity's ID.
        created_at: A datetime object representings when the entity was created.
        updated_at: A datetime object representing when the entity was last updated.
    """

    def __init__(
        self,
        id: Union[int, str, None] = None,
        created_at: Union[datetime, None] = None,
        updated_at: Union[datetime, None] = None,
    ) -> None:
        """Initializes an Entity with given or default values.

        Args:
            id: A Union of int, str, and None representing the entity's ID. Defaults to uuidv4.
            created_at: A Union of datetime and None representing when the entity was created. Defaults to current UTC time.
            updated_at: A Union of datetime and None representing when the entity was last updated. Defaults to current UTC time.
        """

        self.id = id or str(uuid4())
        self.created_at = created_at or datetime.now(tz=timezone.utc)
        self.updated_at = updated_at or datetime.now(tz=timezone.utc)

    def __repr__(self) -> str:
        non_special_attrs = [
            f"{chave}={valor!r}"
            for chave, valor in self.__dict__.items()
            if not isinstance(valor, list) and not isinstance(valor, dict)
        ]
        special_attrs = [
            f"{chave}={valor!r}"
            for chave, valor in self.__dict__.items()
            if isinstance(valor, list) or isinstance(valor, dict)
        ]
        return f"{self.__class__.__name__}({', '.join([*non_special_attrs, *special_attrs])})"

    def to_dict(self) -> T:
        """Converts the entity to a dictionary.

        Returns:
            A dictionary representation of the entity.
        """

        def _serialize(obj, processors: dict[PROCESSORS, Callable]):
            if dataclasses.is_dataclass(obj):
                obj = processors["from_dataclass"](obj)
            if isinstance(obj, Entity):
                obj = processors["from_entity"](obj)
            if isinstance(obj, dict):
                obj = processors["from_dict"](obj)
            if isinstance(obj, list):
                obj = processors["from_list"](obj)
            if isinstance(obj, datetime):
                obj = processors["from_datetime"](obj)
            if isinstance(obj, Enum):
                obj = processors["from_enum"](obj)
            return obj

        processors: dict[PROCESSORS, Callable] = {
            "from_dataclass": lambda x: asdict(x),
            "from_entity": lambda x: x.to_json(),
            "from_dict": lambda x: {k: _serialize(v, processors) for k, v in x.items()},
            "from_list": lambda x: [_serialize(v, processors) for v in x],
            "from_datetime": lambda x: x.isoformat(),
            "from_enum": lambda x: x.value,
        }

        return cast(T, _serialize(self.__dict__, processors))

    def to_json(self, indent: int = 0):
        return json.dumps(self.to_dict(), indent=indent or None, ensure_ascii=False)
