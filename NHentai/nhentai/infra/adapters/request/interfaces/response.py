from dataclasses import dataclass, field
from typing import Any, Dict, Union, List


@dataclass(frozen=True)
class RequestResponse:
    host: str = field(default="")
    status_code: int = field(default=200)
    headers: Dict[str, Any] = field(default_factory=dict)
    text: Union[str, bytes] = field(default='')
    json: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
