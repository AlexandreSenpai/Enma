from .base_dataclass import BaseDataclass
from typing import List
from dataclasses import dataclass

from .doujin import Doujin
# from .links import CharacterLink

@dataclass
class Page(BaseDataclass):
    doujins: List[Doujin]
    total_results: int
    total_pages: int
    per_page: int
    page: int

@dataclass
class SearchResult(BaseDataclass):
    query: str
    sort: str
    page: int
    total_results: int
    total_pages: int
    doujins: List[Doujin]

@dataclass
class GroupListPage(BaseDataclass):
    page: int
    total_pages: int
    groups: List[str]

@dataclass
class CharacterListPage(BaseDataclass):
    page: int
    total_pages: int
    characters: List[str]

@dataclass
class ArtistListPage(BaseDataclass):
    page: int
    total_pages: int
    artists: List[str]

@dataclass
class TagListPage(BaseDataclass):
    page: int
    total_pages: int
    tags: List[str]

@dataclass
class PopularPage(BaseDataclass):
    doujins: List[Doujin]
    total_doujins: int