"""
This module defines the SearchResult entity for the Enma application.
It represents the result of a manga search operation.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict
from enma.domain.entities.manga import Manga
from enma.domain.entities.pagination import Pagination, Thumb

class ISearchResultProps(TypedDict):
    id: int | str
    created_at: datetime
    updated_at: datetime
    page: int
    total_pages: int
    total_results: int
    results: list[Manga]

@dataclass
class SearchResult(Pagination):
    """
    Entity class representing a search result in the Enma application.
    """
    query: str

    def __init__(self,
                 query: str,
                 page: int,
                 total_pages: int = 0,
                 total_results: int = 0,
                 results: list[Thumb] | None = None,
                 id: int | str | None = None, 
                 created_at: datetime | None = None, 
                 updated_at: datetime | None = None):
        
        super().__init__(page=page,
                         total_pages=total_pages,
                         total_results=total_results,
                         results=results,
                         id=id,
                         created_at=created_at,
                         updated_at=updated_at)
        
        self.query = query
        