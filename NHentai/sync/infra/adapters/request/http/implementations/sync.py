from typing import Any, Dict, Union
from urllib import parse

import requests

from NHentai.sync.infra.adapters.request.http.interfaces.request import RequestInterface
from NHentai.sync.infra.adapters.request.http.interfaces.response import RequestResponse


class RequestsAdapter(RequestInterface):
    def parse_params_to_url_safe(self, params: Dict[str, Any]) -> Dict[str, str]:
        return parse.urlencode(params, quote_via=parse.quote)

    def get(self, url: str, params: Union[Dict[str, Any], None]=None, headers: Union[Dict[str, Any], None]=None) -> RequestResponse:
        response = requests.get(f'{url}?{self.parse_params_to_url_safe(params=params) if params else ""}',  
                                headers=headers or {})
        return RequestResponse(status_code=response.status_code, 
                               host=response.url,
                               headers=response.headers, 
                               text=response.text, 
                               json=response.json,
                               history=[redirect.url for redirect in response.history])
        
        