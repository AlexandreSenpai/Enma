[![CodeFactor](https://www.codefactor.io/repository/github/alexandresenpai/nhentai-api/badge)](https://www.codefactor.io/repository/github/alexandresenpai/nhentai-api)
[![PyPI download month](https://img.shields.io/pypi/dm/NHentai-API.svg)](https://pypi.python.org/pypi/NHentai-API/)
[![codecov](https://codecov.io/gh/AlexandreSenpai/NHentai-API/branch/master/graph/badge.svg?token=F3LP15DYMR)](https://codecov.io/gh/AlexandreSenpai/NHentai-API)
[![Python 3.7+](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

# NHentai API

A NHentai API made using python webscrapping
For update notes follow me on [Twitter](https://twitter.com/AlexandreSenpa1).

### Instalation

```bash
 pip install --upgrade NHentai-API
 # or pip3 install --upgrade NHentai-API
```

### Library Features

- Home page pagination,
- Doujin information,
- Random doujin,
- Search by id and tag,
- Character List
- Popular List

### Usage

##### Home

```python
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    random_doujin: HomePage = nhentai.get_pages(page=1)
```

the expected output is a HomePage instance:

```python
    Page(doujins: [DoujinThumbnail(id: str,
                                    title: str,
                                    lang: str,
                                    cover: str,
                                    url: str,
                                    tags: List[str])],
        total_pages: int,
        total_results: int,
        per_page: int)
```

##### Random

```python
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    random_doujin: Doujin = nhentai.get_random()
```

The expected output is a Doujin instance:

```python
    Doujin(id: int
            media_id: str
            upload_at: datetime
            title: List[Title]
            tags: List[Tag]
            artists: List[Tag]
            languages: List[Tag]
            categories: List[Tag]
            characters: List[Tag]
            parodies: List[Tag]
            groups: List[Tag]
            cover: str
            images: List[DoujinPage]
            total_pages: int)
```

It's good always remember that some doujins doesnt have many properties that are listed above like artists, characters, parodies and more. This is only the default Doujin dataclass template.

##### Search

```python
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    search_obj: SearchPage = nhentai.search(query='naruto', sort=Sort.TODAY, page=1)
    search_obj: SearchPage = nhentai.search(query='30955', page=1)
```

expected output:

```python
    SearchPage(query: str
               sort: str
               total_results: int
               total_pages: int
               doujins: [DoujinThumbnail(id: str,
                                         title: str,
                                         lang: str,
                                         cover: str,
                                         url: str,
                                         tags: List[str])])
```

##### Doujin

```python
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    doujin: Doujin = nhentai.get_doujin(id='287167')
```

expected output:

```python
    Doujin(id: int
            media_id: str
            upload_at: datetime
            title: List[Title]
            tags: List[Tag]
            artists: List[Tag]
            languages: List[Tag]
            categories: List[Tag]
            characters: List[Tag]
            parodies: List[Tag]
            groups: List[Tag]
            cover: str
            images: List[DoujinPage]
            total_pages: int)
```

##### Characters

```python
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    doujin: CharacterListPage = nhentai.get_characters(page=1)
```

expected output:

```python
    CharacterListPage(page=int,
                      total_pages=int,
                      characters=[CharacterLink(section: str
                                                title: str
                                                url: str
                                                total_entries: int)])
```

##### Most Popular

```python
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    doujins: PopularPage = nhentai.get_popular_now()
```

expected output:

```python
    PopularPage(doujins=List[DoujinThumbnail(id: str,
                                             title: str,
                                             lang: str,
                                             cover: str,
                                             url: str,
                                             tags: List[str])],
                total_doujins: int)
```

## Introducing NHentai Async

This is the first version of the asynchronous nhentai scrapper. The methods works in the very same way as the base nhentai scrapper, but to make it works you'll have to work with asyncio module using an event loop that you can import from it or get from NHentaiAsync class property: `event_loop`.

Since we're working with async functions, you can only call the NHentaiAsync methods from inside an async funcion or context.

```py
from NHentai import NHentaiAsync

if __name__ == '__main__':
    nhentai_async = NHentaiAsync()
    event_loop = nhentai_async.event_loop
    popular = event_loop.run_until_complete(nhentai_async.get_popular_now())
    print(popular)
```

or even

```python
from NHentai import NHentaiAsync

nhentai_async = NHentaiAsync()

async def get_popular():
    popular = await nhentai_async.get_popular_now()
    print(popular)

if __name__ == '__main__':
    event_loop = nhentai_async.event_loop
    event_loop.run_until_complete(get_popular())
```
