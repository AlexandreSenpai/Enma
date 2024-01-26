from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TypedDict, Union

from enma.domain.entities.base import Entity

class MIME(Enum):
    J = 'jpg'
    P = 'png'
    G = 'gif'

@dataclass
class Image:
    uri: str
    name: str = field(default='image.jpg')
    width: int = field(default=0)
    height: int = field(default=0)
    mime: MIME = field(default=MIME.J)

@dataclass
class Title:
    english: str = field(default='')
    japanese: str = field(default='')
    other: str = field(default='')

class IMangaProps(TypedDict):
    id: Union[int, str]
    created_at: datetime
    updated_at: datetime
    title: Title
    pages_count: int
    pages: list[Image]

@dataclass
class SymbolicLink:
    link: str

@dataclass
class Chapter:
    id: Union[int, str] = field(default=0)
    pages: list[Image] = field(default_factory=list)
    pages_count: int = field(default=0)
    link: Union[SymbolicLink, None] = field(default=None) 

    def __post_init__(self) -> None:
        self.pages_count = len(self.pages)

    def add_page(self, page: Image) -> None:
        self.pages.append(page)
        self.pages_count += 1

@dataclass
class Genre:
    name: str
    id: Union[int, str] = field(default=0)

@dataclass
class Author(Genre):
    ...

class Manga(Entity[IMangaProps]):
    def __init__(self,
                 title: Title,
                 chapters: Union[list[Chapter], None] = None,
                 language: Union[str, None] = None,
                 genres: Union[list[Genre], None] = None,
                 authors: Union[list[Author], None] = None,
                 thumbnail: Union[Image, None] = None,
                 cover: Union[Image, None] = None,
                 id: Union[int, str, None] = None, 
                 created_at: Union[datetime, None] = None, 
                 updated_at: Union[datetime, None] = None):
        
        super().__init__(id=id,
                         created_at=created_at,
                         updated_at=updated_at)
        
        self.title = title
        self.language = language
        self.cover = cover
        self.thumbnail = thumbnail
        self.authors = authors or []
        self.genres = genres or []
        self.chapters = chapters or []

        self.chapters_count = len(self.chapters if self.chapters else [])
