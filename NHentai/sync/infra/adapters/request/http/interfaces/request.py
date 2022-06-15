from typing import Any, Dict, Union
from NHentai.sync.infra.adapters.request.http.interfaces.response import RequestResponse


class RequestInterface:
    def get(self, url: str, params: Union[Dict[str, Any], None]=None, headers: Union[Dict[str, Any], None]=None) -> RequestResponse: ...