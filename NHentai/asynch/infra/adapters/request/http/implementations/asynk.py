from typing import Any, Dict, Union
from urllib import parse

import aiohttp
from aiohttp.client_exceptions import ContentTypeError

from NHentai.asynch.infra.adapters.request.http.interfaces.request import RequestInterface
from NHentai.asynch.infra.adapters.request.http.interfaces.response import RequestResponse
from NHentai.core.handler import ApiError


class RequestsAdapter(RequestInterface):
    
    async def handle_error(self, request: aiohttp.ClientResponse):
        if request.status == 200: return
        
        handlers = {
            500: ApiError.communication_error,
            404: ApiError.not_found,
            403: ApiError.forbidden,
            401: ApiError.unauthorized,
            400: ApiError.bad_request,
            426: ApiError.too_many_requests,
        }
        
        handler = handlers.get(request.status)
        
        if handler is not None:
            raise handler()
        
        raise Exception(f'An unexpected error occoured while making the request to the website! status code: {request.status}')
        
    
    def parse_params_to_url_safe(self, params: Dict[str, Any]) -> Dict[str, str]:
        return parse.urlencode(params, quote_via=parse.quote)

    async def get(self, url: str, params: Union[Dict[str, Any], None]=None, headers: Union[Dict[str, Any], None]=None) -> RequestResponse:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{url}?{self.parse_params_to_url_safe(params=params) if params else ""}',  
                                    headers=headers or {}) as response:

                

                try:
                
                    return RequestResponse(status_code=response.status, 
                                            host=response.url,
                                            headers=response.headers, 
                                            text=await response.text(), 
                                            json=await response.json(),
                                            history=[redirect.url for redirect in response.history])
                
                except ContentTypeError:
                    
                    return RequestResponse(status_code=response.status, 
                                            host=response.url,
                                            headers=response.headers, 
                                            text=await response.text(), 
                                            json=None,
                                            history=[redirect.url for redirect in response.history])
                                           
        