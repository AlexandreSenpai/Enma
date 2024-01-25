from datetime import datetime
import json
from typing import Generic, TypeVar, Union

T = TypeVar('T')


class Entity(Generic[T]):
    """Base class for entities in the domain model.

    This class provides common attributes and methods for all entities.

    Attributes:
        id: A Union of int and str representing the entity's ID.
        created_at: A datetime object representings when the entity was created.
        updated_at: A datetime object representing when the entity was last updated.
    """

    def __init__(self, 
                 id: Union[int, str, None] = None,
                 created_at: Union[datetime, None] = None,
                 updated_at: Union[datetime, None] = None) -> None:
        """Initializes an Entity with given or default values.

        Args:
            id: A Union of int, str, and None representing the entity's ID. Defaults to 0.
            created_at: A Union of datetime and None representing when the entity was created. Defaults to current UTC time.
            updated_at: A Union of datetime and None representing when the entity was last updated. Defaults to current UTC time.
        """

        self.id = id if id is not None else 0
        self.created_at = created_at if created_at is not None else datetime.utcnow()
        self.updated_at = updated_at if updated_at is not None else datetime.utcnow()

    def __repr__(self) -> str:
        attrs = ', '.join([f"{chave}={valor!r}" for chave, valor in self.__dict__.items()])
        return f"{self.__class__.__name__}({attrs})"

    def to_dict(self) -> T:
        """Converts the entity to a dictionary.

        Returns:
            A dictionary representation of the entity.
        """
        return self.__dict__ # type: ignore