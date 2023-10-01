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