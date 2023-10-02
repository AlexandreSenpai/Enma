
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
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
class SearchResult(Entity[ISearchResultProps]):

    query: str
    page: int
    total_pages: int
    total_results: int
    results: list[Thumb]

    def __init__(self,
                 query: str,
                 page: int,
                 total_pages: int,
                 total_results: int,
                 results: list[Thumb],
                 id: int | str | None = None, 
                 created_at: datetime | None = None, 
                 updated_at: datetime | None = None):
        
        super().__init__(id=id,
                         created_at=created_at,
                         updated_at=updated_at)
        
        self.query = query
        self.page = page
        self.total_pages = total_pages
        self.total_results = total_results
        self.results = results
        