"""
This module defines the SearchResult entity for the Enma application.
It represents the result of a manga search operation.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict
from enma.domain.entities.base import Entity
from enma.domain.entities.manga import Image, Manga

@dataclass
class Thumb:
    id: str
    title: str
    cover: Image

class ISearchResultProps(TypedDict):
    id: int | str
    created_at: datetime
    updated_at: datetime
    page: int
    total_pages: int
    total_results: int
    results: list[Manga]

@dataclass
class Pagination(Entity[ISearchResultProps]):
    """
    Entity class representing a search result in the Enma application.
    """
    page: int
    total_pages: int
    total_results: int
    results: list[Thumb]

    def __init__(self,
                 page: int,
                 total_pages: int = 0,
                 total_results: int = 0,
                 results: list[Thumb] | None = None,
                 id: int | str | None = None, 
                 created_at: datetime | None = None, 
                 updated_at: datetime | None = None):
        
        super().__init__(id=id,
                         created_at=created_at,
                         updated_at=updated_at)
        
        self.page = page
        self.results = results or list()
        self.total_pages = total_pages or 1 if len(self.results) <= 20 else total_pages
        self.total_results = total_results or 20 * self.total_pages if self.total_pages > 1 else len(self.results) 
        