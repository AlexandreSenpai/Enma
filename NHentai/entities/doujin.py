from dataclasses import dataclass, field
from typing import List

@dataclass
class Doujin:
    id: str
    title: str
    secondary_title: str
    tags: List[str]
    artists: List[str]
    languages: List[str]
    categories: List[str]
    characters: List[str]
    parodies: List[str]
    groups: List[str]
    images: List[str]
    total_pages: int = 0

@dataclass
class DoujinThumbnail:
    id: str
    title: str
    lang: str
    cover: str
    url: str
    data_tags: list
