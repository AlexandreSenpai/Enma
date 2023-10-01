from abc import ABC, abstractmethod

from enma.domain.entities.Manga import Manga

class IMangaRepository(ABC):
    @abstractmethod
    def get(self,
            identifier: str) -> Manga | None:
        ...
    
    @abstractmethod
    def search(self,
               query: str) -> Manga | None:
        ...