import sys

from .nhentai.infra.entrypoints.lib import NHentai

__all__ = ['nhentai']
__version__ = '2.0.0'

package_name = "nhentai-api"
python_major = "3"
python_minor = "9"

try:
    assert sys.version_info >= (int(python_major), int(python_minor))
except AssertionError:
    raise RuntimeError(f"\033[31m{package_name!r} requires Python {python_major}.{python_minor}+ (You have Python {sys.version})\033[0m")
