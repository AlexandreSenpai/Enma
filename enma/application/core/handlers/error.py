class SourceNotAvailable(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'SOURCE_NOT_AVAILABLE'
        self.desc: str = 'This error occurs when the client chooses nonexistent source.'
        self.critical: bool = False

class Unknown(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.code: str = 'UNKNOWN'
        self.desc: str = 'This error occours when was not possible to determine the error root cause.'
        self.critical: bool = True

class NotFound(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.code: str = 'NOT_FOUND'
        self.desc: str = 'This error occours when was not possible to find the requested resource.'
        self.critical: bool = True

class Forbidden(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.code: str = 'FORBIDDEN'
        self.desc: str = 'This error occours when the client can\'t perform a request to the source due lack of credentials.'
        self.critical: bool = True

class InvalidRequest(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.code: str = 'INVALID_REQUEST'
        self.desc: str = 'This error occours when the client tries to perform an request with wrong data input.'
        self.critical: bool = True

class InvalidResource(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'INVALID_RESOURCE'
        self.desc: str = 'This error occurs when the client tries to perform an action with an invalid resource.'
        self.critical: bool = True

class NhentaiSourceWithoutConfig(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'NHENTAI_SOURCE_WITHOUT_CONFIG'
        self.desc: str = 'This error occurs when the client tries to use Nhentai source with no cloudflare cookie.'
        self.critical: bool = True

class InvalidConfig(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'INVALID_CONFIG'
        self.desc: str = 'This error occurs when client tries to set wrong config object.'
        self.critical: bool = True

class InstanceError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'INSTANCE_ERROR'
        self.desc: str = 'This error occurs when the client tries to create an instance with wrong type.'
        self.critical: bool = True

class SourceWasNotDefined(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'SOURCE_WAS_NOT_DEFINED'
        self.desc: str = 'This error occurs when the client tries to perform Enma operations before of setting a source.'
        self.critical: bool = True

class ExceedRetryCount(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'EXCEED_RETRY_COUNT'
        self.desc: str = 'This error occurs when enma tries perform some action but something went wrong.'
        self.critical: bool = True

class ExceedRateLimit(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'EXCEED_RATE_EXCEED'
        self.desc: str = 'This error occurs when enma perform more requests than a server can handle. Cool down your requests to this source!'
        self.critical: bool = False
