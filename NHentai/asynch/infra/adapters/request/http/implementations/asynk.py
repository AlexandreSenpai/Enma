from typing import Any, Dict, Union
from urllib import parse

import aiohttp
from aiohttp.client_exceptions import ContentTypeError

from NHentai.asynch.infra.adapters.request.http.interfaces.request import RequestInterface
from NHentai.asynch.infra.adapters.request.http.interfaces.response import RequestResponse
from NHentai.core.handler import ApiError
from NHentai.core.helpers.cloudflare import CloudFlareSettings


class RequestsAdapter(RequestInterface):
    
    def __init__(self, request_settings: CloudFlareSettings=None):
        self.request_settings = request_settings
    
    async def handle_error(self, request: aiohttp.ClientResponse):
        if request.status == 200: return
        
        stack = await request.text()
        
        handlers = {
            500: lambda: ApiError.communication_error(message=f'Could not communicate with {request.url}', payload=request.url, stack=stack),
            404: lambda: ApiError.not_found(message=f'Could not find this resource', payload=request.url, stack=stack),
            403: lambda: ApiError.forbidden(message=f'You are not allowed to access this resource', payload=request.url, stack=stack),
            401: lambda: ApiError.unauthorized(message=f'You are not authorized to access this resource', payload=request.url, stack=stack),
            400: lambda: ApiError.bad_request(message=f'Bad request', payload=request.url, stack=stack),
            426: lambda: ApiError.too_many_requests(message=f'Too many requests', payload=request.url, stack=stack),
        }
        
        handler = handlers.get(request.status)
        
        if handler is not None:
            raise handler()
        
        raise Exception(f'An unexpected error occoured while making the request to the website! status code: {request.status}')
        
    
    def parse_params_to_url_safe(self, params: Dict[str, Any]) -> Dict[str, str]:
        return parse.urlencode(params, quote_via=parse.quote)

    async def get(self, url: str, params: Union[Dict[str, Any], None]=None, headers: Union[Dict[str, Any], None]=None) -> RequestResponse:
        cookies = self.request_settings.as_dict() if self.request_settings is not None else None
        print(cookies)
        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.get(f'{url}?{self.parse_params_to_url_safe(params=params) if params else ""}',  
                                    headers=headers or {}) as response:
                filtered = session.cookie_jar.filter_cookies(response.host)
                print(filtered)
                await self.handle_error(request=response)

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
                                           
        