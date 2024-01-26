from abc import ABC, abstractmethod
from io import BytesIO
from enma.domain.entities.manga import Image


class IDownloaderAdapter(ABC):

    @abstractmethod
    def download(self, page: Image) -> BytesIO:
        ...
