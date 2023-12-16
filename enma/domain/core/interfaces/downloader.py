from typing import Callable, TypeAlias


IDownloader: TypeAlias = Callable[[str, str], None]