<p align="center">
    <img src="./docs/images/enma.png" align="center" width="50%">
</p>

<center>

[![PyPI download month](https://img.shields.io/pypi/dm/Enma.svg)](https://pypi.python.org/pypi/Enma/)
[![codecov](https://codecov.io/gh/AlexandreSenpai/Enma/branch/master/graph/badge.svg?token=F3LP15DYMR)](https://codecov.io/gh/AlexandreSenpai/Enma)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![GitHub forks](https://img.shields.io/github/forks/AlexandreSenpai/Enma)](https://github.com/AlexandreSenpai/Enma)
[![GitHub stars](https://img.shields.io/github/stars/AlexandreSenpai/Enma)](https://github.com/AlexandreSenpai/Enma)
[![GitHub issues](https://img.shields.io/github/issues/AlexandreSenpai/Enma)](https://github.com/AlexandreSenpai/Enma/issues)

</center>

# Enma

Enma is a Python library designed to fetch manga and doujinshi data from many sources. It provides a unified interface to interact with different manga repositories, making it easier to retrieve manga details, search for manga, paginate through results, and fetch random manga.

## Requirements

- Python 3.9+

## Installation
```py
pip install enma
```

Ensure you have the required Python version:
```py
import sys

package_name = "enma"
python_major = "3"
python_minor = "9"

try:
    assert sys.version_info >= (int(python_major), int(python_minor))
except AssertionError:
    raise RuntimeError(f"{package_name!r} requires Python {python_major}.{python_minor}+ (You have Python {sys.version})")
```

## Features Comparison

Feature    | NHentai | Manganato
-----------|---------|-----------
search     |    ✅   |     ✅    
random     |    ✅   |     🚫    
get        |    ✅   |     ✅    
paginate   |    ✅   |     ✅
download   |    ✅   |     ✅       
author_page|    ✅   |     🚫       
set_config |    ✅   |     🚫

## Usage

### Example 1: Using Default Available Sources

```py
from typing import cast
from enma import Enma, DefaultAvailableSources, CloudFlareConfig, NHentai, Sort

enma = Enma[DefaultAvailableSources]()

config = CloudFlareConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    cf_clearance=''
)

enma.source_manager.set_source(source_name='nhentai')
nh_source = cast(NHentai, enma.source_manager.source)
nh_source.set_config(config=config)

doujin = enma.random()
print(doujin)
```

### Example 2: Extending with Custom Sources
```py
from typing import cast
from enma import Enma, SourcesEnum, Manganato, IMangaRepository

class AvailableSources(SourcesEnum):
    NHENTAI = 'nhentai'
    MANGANATO = 'manganato'
    NEW_SOURCE = 'new-source'

enma = Enma[AvailableSources]()

enma.source_manager.add_source(source_name='new-source', source=Manganato()) # Source MUST be an instance of IMangaRepository
enma.source_manager.set_source(source_name=AvailableSources.MANGANATO)

manga = enma.random()
print(manga)
```

## Downloading Chapters
Using Enma you're able to download chapter pages to your local storage or any other storage that implements `ISaverAdapter`.

You can check it out how to do it right below:

```py
from enma import (Enma,
                  CloudFlareConfig, 
                  ManganatoDownloader, 
                  Threaded, 
                  LocalStorage)

enma = Enma()
enma.source_manager.set_source('manganato')
manga = enma.get(identifier='manga-wb999684')

downloader = ManganatoDownloader()
local = LocalStorage()

if manga:
    enma.download_chapter(path=f'./download/{manga.title.english}',
                          chapter=manga.chapters[0],
                          downloader=downloader,
                          saver=local,
                          threaded=Threaded(use_threads=True,
                                            number_of_threads=5))
```

## Logger Control
By default Enma sets logs as `SILENT`. But if you're needing to see what Enma outputs you can set log mode as `NORMAL` or `DEBUG` to deep logs.

```py
from enma import logger, LogMode

logger.mode = LogMode.NORMAL
```

## Symbolic Links
Enma normally retrieves all information about a manga, including the pages of each chapter. This process can be slow if the manga has many chapters. To speed it up, you can use symbolic links when getting a manga. This way, Enma creates a SymbolicLink instead of fetching all data immediately. You can then use this link to quickly access and fetch data for a specific chapter later.

```py
from enma import Enma

enma = Enma()

enma.source_manager.set_source('manganato')
doujin = enma.get(identifier='manga-kb951984', with_symbolic_links=True)

# Manga(id='manga-kb951984', 
#       created_at=datetime.datetime(2024, 1, 22, 10, 5), 
#       updated_at=datetime.datetime(2024, 1, 22, 10, 5), 
#       title=Title(english='Monster Musume No Iru Nichijou', 
#                   japanese='モンスター娘のいる日常', 
#                   other='魔物娘的同居日常'), 
#       language=None, 
#       cover=Image(uri='https://avt.mkklcdnv6temp.com/23/p/1-1583464626.jpg', name='image.jpg', width=0, height=0, mime=<MIME.J: 'jpg'>), 
#       thumbnail=Image(uri='https://avt.mkklcdnv6temp.com/23/p/1-1583464626.jpg', name='image.jpg', width=0, height=0, mime=<MIME.J: 'jpg'>), 
#       authors=[Author(name='Okayado', id=0)], 
#       genres=[Genre(name='Comedy', id=0), 
#               Genre(name='Fantasy', id=0), 
#               Genre(name='Harem', id=0)], 
#       chapters=[Chapter(id='chapter-84', pages=[], pages_count=0, link=SymbolicLink(link='https://chapmanganato.to/manga-kb951984/chapter-84')), 
#                 Chapter(id='chapter-83', pages=[], pages_count=0, link=SymbolicLink(link='https://chapmanganato.to/manga-kb951984/chapter-83'))], 
#       chapters_count=95)

if doujin is not None:
    chapter_ref = doujin.chapters[0]
    chapter = enma.fetch_chapter_by_symbolic_link(link=chapter_ref.link)

```

## Retrieving `user-agent` and `cf_clearance` for NHentai

To retrieve the `user-agent` and `cf_clearance` for NHentai:

1. **Open NHentai in your browser**: Navigate to the NHentai website.
2. **Open Developer Tools**:
    - **For Google Chrome**: Right-click on the webpage and select Inspect or simply press Ctrl + Shift + I (or Cmd + Option + I on Mac).
    - **For Firefox**: Right-click on the webpage and select Inspect Element or press Ctrl + Shift + I (or Cmd + Option + I on Mac).
3. **Navigate to the Network Tab**: In the Developer Tools panel, click on the Network tab. This tab captures all network requests made by the webpage.
4. **Reload the Page**: With the Network tab open, reload the NHentai website by pressing Ctrl + R (or Cmd + R on Mac). This ensures that all network requests are captured.
5. **Select the nhentai.net Request**: After reloading, you'll see a list of files on the left side of the Network tab. Click on the first file named nhentai.net. This represents the main request to the NHentai website.
6. **Find the Request Headers**: On the right side, you'll see several tabs like Headers, Preview, Response, etc. Make sure you're on the Headers tab. Scroll down until you find a section named Request Headers.
7. **Copy the user-agent and cf_clearance**:
    - **user-agent**: This is a string that tells the server which web browser is being used. Look for an entry named User-Agent and copy its value.
    - **cf_clearance**: This is a specific cookie set by CloudFlare for security purposes. Look for an entry named cf_clearance and copy its value.

![example](./docs/images/user-agent.png)
## Example:

```py
config = CloudFlareConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    cf_clearance=''
)
```
> **Note**: The user-agent and cf_clearance values can change over time. If you encounter issues accessing NHentai through the Enma library, you might need to repeat the above steps to get updated values.

## Errors

While using the library, you might encounter some specific errors. Here's a description of each:

1. **InstanceError**: 
    - **Description**: Raised when an instance of an object is not of the expected type.
    - **Common Cause**: Trying to add a source that isn't an instance of `IMangaRepository`.

2. **SourceNotAvailable**: 
    - **Description**: Raised when attempting to access a source that isn't available in the defined source list.
    - **Common Cause**: Trying to set a source that hasn't been previously added.

3. **SourceWasNotDefined**: 
    - **Description**: Raised when trying to perform an action (like fetching a manga) without first defining a source.
    - **Common Cause**: Forgetting to set the source before performing an operation.

4. **ExceedRetryCount**: 
    - **Description**: Specific to the `NHentai` adapter. Raised when the `random` method fails to fetch a random doujin after several attempts.
    - **Common Cause**: Consecutive failures when trying to fetch a random doujin from NHentai.

5. **NhentaiSourceWithoutConfig**: 
    - **Description**: Raised when trying to make a request to NHentai without providing the necessary configurations.
    - **Common Cause**: Forgetting to provide the `user-agent` and `cf_clearance` when configuring the NHentai adapter.

6. **InvalidResource**: 
    - **Description**: Raised when trying to perform an action with an invalid or inexistent resource.
    - **Common Cause**: Providing an inexistent folder path to downloader.

7. **InvalidRequest**:
    - **Description**: Raised when trying to perform an action with an invalid data type.
    - **Common Cause**: Making an action with wrong parameter data type.

When encountering one of these errors, refer to the description and common cause to assist in troubleshooting.

## Future Plans

We are actively working on introducing an asynchronous version of the Enma library to better cater to applications that require non-blocking operations. This version will be maintained in a separate repository to keep the core library lightweight. However, for ease of access and installation, you'll be able to install the asynchronous version directly using:

```bash
pip install enma[async]
```
Stay tuned for updates and ensure to check our repository for the latest advancements!
## Frequently Asked Questions (FAQ)

**Q: Can I add more sources to Enma?**</br>
A: Yes! Enma is designed to be extensible. You can add more sources by extending the `SourcesEnum` and implementing `IMangaRepository` that contains the required methods for the new source.

**Q: I'm facing issues with a specific source. What should I do?**</br>
A: Ensure you have the latest version of Enma. If the issue persists, please raise an issue on our GitHub repository detailing the problem.

**Q: How often is Enma updated?**</br>
A: Enma is updated regularly as new sources are added or when there are significant changes to existing sources.

## Contributing

We welcome contributions! If you'd like to contribute:

1. Fork the repository.
2. Make your changes.
3. Submit a pull request.

Ensure you follow the coding standards and write tests for new features.

## License

MIT
