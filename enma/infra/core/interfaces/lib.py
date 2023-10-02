from abc import ABC, abstractmethod

from enma.domain.entities.search_result import SearchResult

class IEnma(ABC):
    @abstractmethod
    def get(self, identifier: str):
        ...
    
    def search(self, query: str, **kwargs) -> SearchResult:
        ...