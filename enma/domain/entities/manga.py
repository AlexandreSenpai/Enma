from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os
from typing import Optional, TypedDict

from enma.application.core.handlers.error import InvalidResource
from enma.domain.core.interfaces.downloader import IDownloader
from enma.domain.entities.base import Entity

class MIME(Enum):
    J = 'jpg'
    P = 'png'
    G = 'gif'

@dataclass
class Image:
    uri: str
    width: int = field(default=0)
    height: int = field(default=0)
    mime: MIME = field(default=MIME.J)

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

    def download(self, downloader: IDownloader, output_path: Optional[str] = None) -> None:
        if output_path is None: 
            output_path = './downloads'
            os.makedirs(output_path, exist_ok=True)

        if output_path and not os.path.isdir(output_path):
            raise InvalidResource('This directory does not exists.')
        
        for i, page in enumerate(self.pages):
            image_path = os.path.join(output_path, f'{i}.{page.mime.value}')
            downloader(page.uri, image_path)

@dataclass
class Genre:
    name: str
    id: str | int = field(default=0)

@dataclass
class Manga(Entity[IMangaProps]):

    title: Title
    authors: list[str]
    genres: list[Genre]
    chapters: list[Chapter]
    chapters_count: int
    cover: Image | None
    thumbnail: Image | None

    def __init__(self,
                 title: Title,
                 chapters: list[Chapter],
                 genres: list[Genre] | None = None,
                 authors: list[str] | None = None,
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
        self.authors = authors or []
        self.genres = genres or []