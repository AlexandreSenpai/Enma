from io import BytesIO
import random
import requests

from enma.application.core.interfaces.downloader_adapter import IDownloaderAdapter
from enma.domain.entities.manga import Image


class DefaultDownloader(IDownloaderAdapter):
    def download(self, page: Image) -> BytesIO:
        response = requests.get(url=page.uri)
        return BytesIO(response.content)
