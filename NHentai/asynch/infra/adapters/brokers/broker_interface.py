from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')

class BrokerInterface(ABC, Generic[T]):
    @abstractmethod
    def publish(self, message: T) -> str: ...