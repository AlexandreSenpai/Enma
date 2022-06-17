[![CodeFactor](https://www.codefactor.io/repository/github/alexandresenpai/nhentai-api/badge)](https://www.codefactor.io/repository/github/alexandresenpai/nhentai-api)
[![PyPI download month](https://img.shields.io/pypi/dm/NHentai-API.svg)](https://pypi.python.org/pypi/NHentai-API/)
[![codecov](https://codecov.io/gh/AlexandreSenpai/NHentai-API/branch/dev/graph/badge.svg?token=F3LP15DYMR)](https://codecov.io/gh/AlexandreSenpai/NHentai-API)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

# NHentai API

A NHentai API made using python webscrapping. \
For update notes follow me on [Twitter](https://twitter.com/AlexandreSenpa1) or join on NHentai-API [discord server](https://discord.gg/576uSRDD)

## Installation
```bash
pip install --upgrade NHentai-API
```
or
```
pip3 install --upgrade NHentai-API
```

## Library Features
- Home page pagination;
- Doujin information;
- Random doujin;
- Search;
- Comment Listing;
- Today's Popular Doujins.

### Home

```python
from NHentai import NHentai

nhentai = NHentai()
random_doujin: HomePage = nhentai.get_pages(page=1)
```
The expected output is a HomePage instance:
```python
Page(
    doujins: List[
        Doujin(
            id: int
            media_id: str
            upload_at: datetime
            url: str
            title: List[Title]
            tags: List[Tag]
            artists: List[Tag]
            languages: List[Tag]
            categories: List[Tag]
            characters: List[Tag]
            parodies: List[Tag]
            groups: List[Tag]
            cover: Cover
            images: List[DoujinPage]
            total_favorites: int = 0
            total_pages: int = 0
        )
    ],
    total_pages: int,
    total_results: int,
    per_page: int)
```

### Random
```python
from NHentai import NHentai

nhentai = NHentai()
random_doujin: Doujin = nhentai.get_random()
```
The expected output is a Doujin instance:
```python
Doujin(
    id: int
    media_id: str
    upload_at: datetime
    url: str
    title: List[Title]
    tags: List[Tag]
    artists: List[Tag]
    languages: List[Tag]
    categories: List[Tag]
    characters: List[Tag]
    parodies: List[Tag]
    groups: List[Tag]
    cover: Cover
    images: List[DoujinPage]
    total_favorites: int = 0
    total_pages: int = 0
)
```
Note: Not all doujins have certain properties like `tags`, `artists`, etc. They could be an empty list or a NoneType value.

### Search
```python
from NHentai import NHentai, Sort

nhentai = NHentai()
search_obj: SearchPage = nhentai.search(query='naruto', sort=Sort.RECENT, page=1)
search_obj: SearchPage = nhentai.search(query='30955', page=1)
```
The expected output is a SearchPage instance:
```python
SearchPage(
    query: str
    sort: str
    total_results: int
    total_pages: int
    doujins: List[
        Doujin(
            id: int
            media_id: str
            upload_at: datetime
            url: str
            title: List[Title]
            tags: List[Tag]
            artists: List[Tag]
            languages: List[Tag]
            categories: List[Tag]
            characters: List[Tag]
            parodies: List[Tag]
            groups: List[Tag]
            cover: Cover
            images: List[DoujinPage]
            total_favorites: int = 0
            total_pages: int = 0
        )
    ]
)
```

### Doujin
```python
from NHentai import NHentai

nhentai = NHentai()
doujin: Doujin = nhentai.get_doujin(doujin_id=287167)
```
The expected output is a Doujin instance:
```python
Doujin(
    id: int
    media_id: str
    upload_at: datetime
    url: str
    title: List[Title]
    tags: List[Tag]
    artists: List[Tag]
    languages: List[Tag]
    categories: List[Tag]
    characters: List[Tag]
    parodies: List[Tag]
    groups: List[Tag]
    cover: Cover
    images: List[DoujinPage]
    total_favorites: int = 0
    total_pages: int = 0
)
```

### Comments
```python
from NHentai import NHentai

nhentai = NHentai()
comments: CommentPage = nhentai.get_comments(doujin_id=1)
```
The expected output is a CharacterListPage instance:
```python
CommentPage(total_comments: int
            comments: List[Comment(id: int, 
                                   gallery_id: int, 
                                   poster=User(id: int, 
                                               username: str, slug: str, 
                                               avatar_url: str, 
                                               is_superuser: bool, 
                                               is_staff: bool), 
                                    post_date: str, 
                                    body: str)])
```

### Most Popular
```python
from NHentai import NHentai

nhentai = NHentai()
doujins: PopularPage = nhentai.get_popular_now()
```
The expected output is a PopularPage instance:
```python
PopularPage(
    total_doujins: int
    doujins: List[
        Doujin(
            id: int
            media_id: str
            upload_at: datetime
            url: str
            title: List[Title]
            tags: List[Tag]
            artists: List[Tag]
            languages: List[Tag]
            categories: List[Tag]
            characters: List[Tag]
            parodies: List[Tag]
            groups: List[Tag]
            cover: Cover
            images: List[DoujinPage]
            total_favorites: int = 0
            total_pages: int = 0
        )
    ],
)
```

# NHentai API Async

This is the first version of the asynchronous nhentai scrapper. The methods work in the very same way as the base nhentai scrapper, but to make it work you'll have to work with asyncio module using an event loop that you can import from it or get from NHentaiAsync class property: `event_loop`.

Since we're working with async functions, you can only call the NHentaiAsync methods from inside an async funcion or context.
If you are already working in an async event loop, such as a python Discord API like `discord.py`, you can simply await calls that you would otherwise have to call `run_until_complete` on top of.

Async example 1:
```py
from NHentai import NHentaiAsync

nhentai_async = NHentaiAsync()
event_loop = nhentai_async.event_loop
popular = event_loop.run_until_complete(nhentai_async.get_popular_now())
print(popular)
```
Async example 2:
```python
from NHentai import NHentaiAsync

nhentai_async = NHentaiAsync()

async def get_popular():
    popular = await nhentai_async.get_popular_now()
    print(popular)

event_loop = nhentai_async.event_loop
event_loop.run_until_complete(get_popular())
```

Await example:
```python
from NHentai import NHentaiAsync
nhentai_async = NHentaiAsync()

# Run in an async function or you will get an error: `'await' outside async function`.
popular = await nhentai_async.get_popular_now()
print(popular)
```

