from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO

@dataclass
class File:
    name: str
    data: BytesIO

class ISaverAdapter(ABC):

    @abstractmethod
    def save(self, path: str, file: File) -> bool:
        ...
