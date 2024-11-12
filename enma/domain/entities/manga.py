from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal, TypedDict, Union

from enma.domain.entities.base import Entity

class MIME(Enum):
    JPG = 'jpg'
    J = 'jpg'
    PNG = 'png'
    P = 'png'
    GIF = 'gif'
    G = 'gif'
    W = 'webp'
    WEBP = 'webp'
    
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
    url: str
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
class Unit:
    name: str

@dataclass
class Tag(Unit):
    type: Union[Literal["character"], 
                Literal["related"], 
                Literal["category"]]
    id: Union[int, str] = field(default=0)

@dataclass
class Author(Unit):
    id: Union[int, str] = field(default=0)

@dataclass
class Genre(Unit):
    id: Union[int, str] = field(default=0)

class ILanguage(TypedDict):
    ja: Literal['japanese']
    jp: Literal['japanese']
    japanese: Literal['japanese']
    portuguese: Literal['portuguese']
    pt: Literal['portuguese']
    pt_br: Literal['portuguese']
    english: Literal['english']
    en: Literal['english']
    en_us: Literal['english']
    chinese: Literal['chinese']
    cn: Literal['chinese']
    zh: Literal['chinese']
    russian: Literal['russian']
    ru: Literal['russian']
    turkish: Literal['turkish']
    tr: Literal['turkish']
    spanish: Literal['spanish']
    es_la: Literal['spanish']
    malay: Literal['malay']
    ms: Literal['malay']
    korean: Literal['korean']
    ko: Literal['korean']

Language: ILanguage = {
    'ja': 'japanese',
    'jp': 'japanese',
    'japanese': 'japanese',
    'portuguese': 'portuguese',
    'pt': 'portuguese',
    'pt_br': 'portuguese',
    'english': 'english',
    'en': 'english',
    'en_us': 'english',
    'chinese': 'chinese',
    'cn': 'chinese',
    'zh': 'chinese',
    'ru': 'russian',
    'russian': 'russian',
    'turkish': 'turkish',
    'tr': 'turkish',
    'spanish': 'spanish',
    'es_la': 'spanish',
    'malay': 'malay',
    'ms': 'malay',
    'korean': 'korean',
    'ko': 'korean'
}
    
class Manga(Entity[IMangaProps]):
    def __init__(self,
                 title: Title,
                 status: Literal['ongoing', 'completed'],
                 url: str,
                 chapters: Union[list[Chapter], None] = None,
                 language: Union[str, None] = None,
                 genres: Union[list[Genre], None] = None,
                 tags: Union[list[Tag], None] = None,
                 authors: Union[list[Author], None] = None,
                 thumbnail: Union[Image, None] = None,
                 cover: Union[Image, None] = None,
                 id: Union[int, str, None] = None, 
                 created_at: Union[datetime, None] = None, 
                 updated_at: Union[datetime, None] = None):
        
        super().__init__(id=id,
                         created_at=created_at,
                         updated_at=updated_at)
        
        self.status = status
        self.title = title
        self.language = language
        self.cover = cover
        self.url = url
        self.thumbnail = thumbnail
        self.authors = authors or []
        self.genres = genres or []
        self.chapters = chapters or []
        self.tags = tags or []

        self.chapters_count = len(self.chapters if self.chapters else [])

    def add_chapter(self,
                    chapter: Chapter):
        self.chapters.append(chapter)
        self.chapters_count += 1
