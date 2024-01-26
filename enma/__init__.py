import sys
from enma.application.core.utils.logger import LogMode, logger
from enma.application.use_cases.download_chapter import Threaded
from enma.infra.entrypoints.lib import Enma, SourcesEnum, DefaultAvailableSources
from enma.infra.adapters.repositories.nhentai import CloudFlareConfig, NHentai, Sort
from enma.infra.adapters.repositories.manganato import Manganato
from enma.infra.adapters.downloaders.default import DefaultDownloader
from enma.infra.adapters.downloaders.manganato import ManganatoDownloader
from enma.application.core.interfaces.downloader_adapter import IDownloaderAdapter
from enma.application.core.interfaces.saver_adapter import ISaverAdapter
from enma.infra.adapters.storage.local import LocalStorage
from enma.domain.entities.manga import Manga
from enma.domain.entities.search_result import SearchResult
from enma.domain.entities.pagination import Pagination
from enma.domain.entities.author_page import AuthorPage

package_name = "enma"
python_major = "3"
python_minor = "9"

logger.mode = LogMode.SILENT

try:
    assert sys.version_info >= (int(python_major), int(python_minor))
except AssertionError:
    raise RuntimeError(f"\033[31m{package_name!r} requires Python {python_major}.{python_minor}+ (You have Python {sys.version})\033[0m")
