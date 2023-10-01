
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TypedDict
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
    english: str
    japanese: str
    other: str

class IMangaProps(TypedDict):
    id: int | str
    created_at: datetime
    updated_at: datetime
    title: Title
    pages_count: int
    pages: list[Image]

@dataclass
class Manga(Entity[IMangaProps]):

    title: Title
    pages: list[Image]
    pages_count: int
    cover: Image
    thumbnail: Image

    def __init__(self,
                 title: Title,
                 pages: list[Image],
                 thumbnail: Image,
                 cover: Image,
                 id: int | str | None = None, 
                 created_at: datetime | None = None, 
                 updated_at: datetime | None = None):
        
        super().__init__(id=id,
                         created_at=created_at,
                         updated_at=updated_at)
        
        self.title = title
        self.pages = pages
        self.thumbnail = thumbnail
        self.cover = cover
        self.pages_count = len(self.pages if self.pages else [])
        