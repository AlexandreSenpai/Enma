from abc import ABC, abstractmethod
from typing import Any, Union
from enma.domain.entities.author_page import AuthorPage

from enma.domain.entities.manga import Chapter, Manga, SymbolicLink
from enma.domain.entities.pagination import Pagination
from enma.domain.entities.search_result import SearchResult

class IMangaRepository(ABC):

    @abstractmethod
    def set_config(self, 
                   config: Any) -> None:
        ...

    @abstractmethod
    def get(self,
            identifier: str,
            with_symbolic_links: bool) -> Union[Manga, None]:
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

    @abstractmethod
    def author_page(self,
                    author: str,
                    page: int) -> AuthorPage:
        ...

    @abstractmethod
    def fetch_chapter_by_symbolic_link(self,
                                       link: SymbolicLink) -> Chapter:
        ...
