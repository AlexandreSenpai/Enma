"""
This module defines the core interfaces for the Enma application's infrastructure layer.
It provides abstract classes and methods that need to be implemented by the concrete classes.
"""
from abc import ABC, abstractmethod

from enma.domain.entities.manga import Manga
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