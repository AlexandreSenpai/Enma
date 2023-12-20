import sys
from enma.infra.entrypoints.lib import Enma, SourcesEnum, DefaultAvailableSources
from enma.infra.adapters.repositories.nhentai import CloudFlareConfig, NHentai, Sort
from enma.infra.adapters.repositories.manganato import Manganato
from enma.infra.adapters.downloaders.default import default_downloader
from enma.infra.adapters.downloaders.manganato import manganato_downloader
from enma.domain.core.interfaces.downloader import IDownloader

package_name = "enma"
python_major = "3"
python_minor = "9"

try:
    assert sys.version_info >= (int(python_major), int(python_minor))
except AssertionError:
    raise RuntimeError(f"\033[31m{package_name!r} requires Python {python_major}.{python_minor}+ (You have Python {sys.version})\033[0m")
