
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, TypedDict
from enma.domain.entities.base import Entity

@dataclass
class Image:
    uri: str
    width: int
    height: int

class MIME(Enum):
    J = 'jpg'
    P = 'png'
    G = 'gif'

@dataclass
class Title:
    english: str = field(default='')
    japanese: str = field(default='')
    other: str = field(default='')

class IMangaProps(TypedDict):
    id: int | str
    created_at: datetime
    updated_at: datetime
    title: Title
    pages_count: int
    pages: list[Image]

@dataclass
class Chapter:
    id: str | int
    pages: list[Image] = field(default_factory=list)

    def add_page(self, page: Image) -> None:
        self.pages.append(page)

@dataclass
class Manga(Entity[IMangaProps]):

    title: Title
    author: str | None
    genres: list[str]
    chapters: list[Chapter]
    chapters_count: int
    cover: Image | None
    thumbnail: Image | None

    def __init__(self,
                 title: Title,
                 chapters: list[Chapter],
                 genres: list[str] | None = None,
                 author: str | None = None,
                 thumbnail: Image | None = None,
                 cover: Image | None = None,
                 id: int | str | None = None, 
                 created_at: datetime | None = None, 
                 updated_at: datetime | None = None):
        
        super().__init__(id=id,
                         created_at=created_at,
                         updated_at=updated_at)
        
        self.title = title
        self.chapters = chapters
        self.thumbnail = thumbnail
        self.cover = cover
        self.chapters_count = len(self.chapters if self.chapters else [])
        self.author = author
        self.genres = genres or []
        