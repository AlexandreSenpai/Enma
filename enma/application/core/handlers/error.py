class SourceNotAvailable(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'SOURCE_NOT_AVAILABLE'
        self.desc: str = 'This error occurs when the client chooses nonexistent source.'
        self.critical: bool = False

class NhentaiSourceWithoutConfig(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message: str = message
        self.code: str = 'NHENTAI_SOURCE_WITHOUT_CONFIG'
        self.desc: str = 'This error occurs when the client tries to use Nhentai source with no cloudflare cookie.'
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