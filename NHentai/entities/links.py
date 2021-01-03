from dataclasses import dataclass

@dataclass
class CharacterLink:
    section: str
    title: str
    url: str
    total_entries: int
