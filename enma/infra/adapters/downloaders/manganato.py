from io import BytesIO
import requests

from enma.application.core.interfaces.downloader_adapter import IDownloaderAdapter
from enma.domain.entities.manga import Image

class ManganatoDownloader(IDownloaderAdapter):
    def download(self, page: Image) -> BytesIO:
        response = requests.get(url=page.uri,
                                headers={'Referer': 'https://chapmanganato.com/'})
        return BytesIO(response.content)
