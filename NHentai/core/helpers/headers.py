from attr import field
from dataclasses import dataclass

@dataclass(frozen=True)
class HeadersSettings:
    useragent: str = field()

    def as_dict(self):
        return {"User-Agent": self.useragent}