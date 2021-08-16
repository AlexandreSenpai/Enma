from dataclasses import dataclass
from NHentai.entities.base_entity import BaseClass

@dataclass
class CharacterLink(BaseClass):
    section: str
    title: str
    url: str
    total_entries: int
