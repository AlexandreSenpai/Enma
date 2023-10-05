from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

K = TypeVar('K')
V = TypeVar('V')

@dataclass
class DTO(Generic[K]):
    data: K

class IUseCase(ABC, Generic[K, V]):
    @abstractmethod
    def execute(self, dto: Optional[DTO[K]] = None) -> V:
        ...
