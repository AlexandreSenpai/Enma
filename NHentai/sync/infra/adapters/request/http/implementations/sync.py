from typing import Any, Dict, Union
from urllib import parse

import requests

from NHentai.core.handler import ApiError
from NHentai.core.helpers.cloudflare import CloudFlareSettings
from NHentai.sync.infra.adapters.request.http.interfaces.request import RequestInterface
from NHentai.sync.infra.adapters.request.http.interfaces.response import RequestResponse


class RequestsAdapter(RequestInterface):
    
    def __init__(self, request_settings: CloudFlareSettings=None):
        self.request_settings = request_settings
        
    def parse_params_to_url_safe(self, params: Dict[str, Any]) -> Dict[str, str]:
        return parse.urlencode(params, quote_via=parse.quote)
    
    def handle_error(self, request: requests.Response):
        if request.status_code == 200: return
        
        handlers = {
            500: lambda: ApiError.communication_error(message=f'Could not communicate with {request.url}', payload=request.url, stack=request.text),
            404: lambda: ApiError.not_found(message=f'Could not find this resource', payload=request.url, stack=request.text),
            403: lambda: ApiError.forbidden(message=f'You are not allowed to access this resource', payload=request.url, stack=request.text),
            401: lambda: ApiError.unauthorized(message=f'You are not authorized to access this resource', payload=request.url, stack=request.text),
            400: lambda: ApiError.bad_request(message=f'Bad request', payload=request.url, stack=request.text),
            426: lambda: ApiError.too_many_requests(message=f'Too many requests', payload=request.url, stack=request.text),
        }
        
        handler = handlers.get(request.status_code)
        
        if handler is not None:
            raise handler()
        
        raise Exception(f'An unexpected error occoured while making the request to the website! status code: {request.status}')
        

    def get(self, url: str, params: Union[Dict[str, Any], None]=None, headers: Union[Dict[str, Any], None]=None) -> RequestResponse:
        cookies = self.request_settings.as_dict() if self.request_settings is not None else None
        with requests.Session() as session:
            response = session.get(f'{url}?{self.parse_params_to_url_safe(params=params) if params else ""}',  
                                    headers=headers or {},
                                    cookies=cookies)
            
            self.handle_error(response)
            
            return RequestResponse(status_code=response.status_code, 
                                host=response.url,
                                headers=response.headers, 
                                text=response.text, 
                                json=response.json,
                                history=[redirect.url for redirect in response.history])
            
        