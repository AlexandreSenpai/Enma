from abc import ABC, abstractmethod

from enma.domain.entities.manga import Manga
from enma.domain.entities.pagination import Pagination
from enma.domain.entities.search_result import SearchResult

class IMangaRepository(ABC):
    @abstractmethod
    def get(self,
            identifier: str) -> Manga | None:
        ...
    
    @abstractmethod
    def search(self,
               query: str,
               page: int,
               **kwargs) -> SearchResult:
        ...

    @abstractmethod
    def paginate(self,
                 page: int) -> Pagination: ...
    
    @abstractmethod
    def random(self) -> Manga:
        ...