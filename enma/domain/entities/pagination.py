"""
This module defines the SearchResult entity for the Enma application.
It represents the result of a manga search operation.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict, Union
from enma.domain.entities.base import Entity
from enma.domain.entities.manga import Image, Manga

@dataclass
class Thumb:
    id: str
    url: str
    title: str
    cover: Image

class ISearchResultProps(TypedDict):
    id: Union[int, str]
    created_at: datetime
    updated_at: datetime
    page: int
    total_pages: int
    total_results: int
    results: list[Manga]

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
                 results: Union[list[Thumb], None] = None,
                 id: Union[int, str, None] = None, 
                 created_at: Union[datetime, None] = None, 
                 updated_at: Union[datetime, None] = None):
        
        super().__init__(id=id,
                         created_at=created_at,
                         updated_at=updated_at)
        
        self.page = page
        self.results = results or list()
        self.total_pages = total_pages
        self.total_results = total_results

    def add_result(self, result: Thumb):
        self.results.append(result)