"""
This module defines the SearchResult entity for the Enma application.
It represents the result of a manga search operation.
"""
from datetime import datetime
from typing import TypedDict, Union
from enma.domain.entities.manga import Manga
from enma.domain.entities.pagination import Pagination, Thumb

class ISearchResultProps(TypedDict):
    id: Union[int, str]
    created_at: datetime
    updated_at: datetime
    page: int
    total_pages: int
    total_results: int
    results: list[Manga]

class AuthorPage(Pagination):
    """
    Entity class representing a search result in the Enma application.
    """
    author: str

    def __init__(self,
                 author: str,
                 page: int,
                 total_pages: int = 0,
                 total_results: int = 0,
                 results: Union[list[Thumb], None] = None,
                 id: Union[int, str, None] = None, 
                 created_at: Union[datetime, None] = None, 
                 updated_at: Union[datetime, None] = None):
        
        super().__init__(page=page,
                         total_pages=total_pages,
                         total_results=total_results,
                         results=results,
                         id=id,
                         created_at=created_at,
                         updated_at=updated_at)
        
        self.author = author
