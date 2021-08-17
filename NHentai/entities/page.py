from .base_entity import BaseClass
from typing import List
from dataclasses import dataclass

from .doujin import Doujin, DoujinThumbnail

@dataclass
class Page(BaseClass):
    doujins: List[DoujinThumbnail]
    total_results: int
    total_pages: int
    per_page: int
    page: int

@dataclass
class SearchPage(BaseClass):
    query: str
    sort: str
    total_results: int
    total_pages: int
    doujins: List[DoujinThumbnail]

@dataclass
class GroupListPage(BaseClass):
    page: int
    total_pages: int
    groups: List[str]

@dataclass
class CharacterListPage(BaseClass):
    page: int
    total_pages: int
    characters: List[str]

@dataclass
class ArtistListPage(BaseClass):
    page: int
    total_pages: int
    artists: List[str]

@dataclass
class TagListPage(BaseClass):
    page: int
    total_pages: int
    tags: List[str]

@dataclass
class PopularPage(BaseClass):
    doujins: List[DoujinThumbnail]
    total_doujins: int