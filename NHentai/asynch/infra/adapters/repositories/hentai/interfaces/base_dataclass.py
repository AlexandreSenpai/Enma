from dataclasses import dataclass, asdict


@dataclass
class BaseDataclass:
    def to_dict(self):
        return asdict(self)