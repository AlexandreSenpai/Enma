"""
This module defines the core interfaces for the Enma application's infrastructure layer.
It provides abstract classes and methods that need to be implemented by the concrete classes.
"""
from abc import ABC, abstractmethod
from enma.application.core.interfaces.downloader_adapter import IDownloaderAdapter
from enma.application.core.interfaces.saver_adapter import ISaverAdapter
from enma.application.use_cases.download_chapter import Threaded
from enma.domain.entities.author_page import AuthorPage

from enma.domain.entities.manga import Chapter, Manga
from enma.domain.entities.pagination import Pagination
from enma.domain.entities.search_result import SearchResult

class IEnma(ABC):
    @abstractmethod
    def get(self, identifier: str) -> Manga:
        ...
    
    @abstractmethod
    def search(self, query: str, page: int, **kwargs) -> SearchResult:
        ...
    
    @abstractmethod
    def paginate(self, page: int) -> Pagination:
        ...

    @abstractmethod
    def random(self) -> Manga:
        ...

    def download_chapter(self,
                         path: str,
                         chapter: Chapter,
                         downloader: IDownloaderAdapter,
                         saver: ISaverAdapter,
                         threaded: Threaded) -> None:
        ...
    
    def author_page(self,
                    author: str,
                    page: int) -> AuthorPage: 
        ...