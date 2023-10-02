from abc import ABC, abstractmethod

from enma.domain.entities.manga import Manga
from enma.domain.entities.search_result import SearchResult

class IMangaRepository(ABC):
    @abstractmethod
    def get(self,
            identifier: str) -> Manga | None:
        ...
    
    @abstractmethod
    def search(self,
               query: str,
               **kwargs) -> SearchResult:
        ...