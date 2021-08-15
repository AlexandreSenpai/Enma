import sys

from . import entities
from . import nhentai
from . import nhentai_async

__all__ = ['nhentai', 'nhentai_async', 'entities']
__version__ = '0.0.16'

package_name = "nhentai-api"
python_major = "3"
python_minor = "7"

try:
    assert sys.version_info >= (int(python_major), int(python_minor))
except AssertionError:
    raise RuntimeError(f"\033[31m{package_name!r} requires Python {python_major}.{python_minor}+ (You have Python {sys.version})\033[0m")

NHentai = nhentai.NHentai
NHentaiAsync = nhentai_async.NHentaiAsync
