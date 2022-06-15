from typing import Dict, Any

class ApiError(Exception):
    def __init__(self, message: str, status_code: int=None, stack: Dict[str, Any]=None, payload: Dict[str, Any]=None):
        super().__init__(message)
        self.status_code = status_code or 500
        self.message = message or ""
        self.stack = stack or {}
        self.payload = payload or {}
    
    @staticmethod
    def internal_server_error(message: str=None, stack: str=None, payload: Dict[str, Any]=None):
        return ApiError(message=message or "Internal Server Error", stack=stack, payload=payload)
    
    @staticmethod
    def bad_request(message: str=None, stack: str=None, payload: Dict[str, Any]=None):
        return ApiError(message=message or "Bad Request", stack=stack, payload=payload)
    
    @staticmethod
    def unauthorized(message: str=None, stack: str=None, payload: Dict[str, Any]=None):
        return ApiError(message=message or "Unauthorized", stack=stack, payload=payload)
    
    @staticmethod
    def forbidden(message: str=None, stack: str=None, payload: Dict[str, Any]=None):
        return ApiError(message=message or "Forbidden", stack=stack, payload=payload)
    
    @staticmethod
    def not_found(message: str=None, stack: str=None, payload: Dict[str, Any]=None):
        return ApiError(message=message or "Not Found", stack=stack, payload=payload)
    
    @staticmethod
    def too_many_requests(message: str=None, stack: str=None, payload: Dict[str, Any]=None):
        return ApiError(message=message or "Too Many Requests", stack=stack, payload=payload)
    
    @staticmethod
    def communication_error(message: str=None, stack: str=None, payload: Dict[str, Any]=None):
        return ApiError(message=message or "Communication Error", stack=stack, payload=payload)