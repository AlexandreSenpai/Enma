from dataclasses import asdict, dataclass

from attr import field

@dataclass(frozen=True)
class CloudFlareSettings:
    cf_clearance: str = field()
    csrftoken: str = field()
    
    def as_dict(self):
        return asdict(self)