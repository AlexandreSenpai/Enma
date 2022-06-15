from typing import Any, Dict, Union
from NHentai.asynch.infra.adapters.request.http.interfaces.response import RequestResponse


class RequestInterface:
    async def get(self, url: str, params: Union[Dict[str, Any], None]=None, headers: Union[Dict[str, Any], None]=None) -> RequestResponse: ...