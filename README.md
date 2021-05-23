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
from NHentai.nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    random_doujin: HomePage = nhentai.get_pages(page=1)
```

the expected output is a HomePage instance:
```python
    HomePage(doujins: [DoujinThumbnail(id: str,
                                       title: str,
                                       lang: str,
                                       cover: str,
                                       url: str,
                                       data_tags: List[str])], 
             total_pages: int)
```

##### Random

```python
from NHentai.nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    random_doujin: Doujin = nhentai.get_random()
```

The expected output is a Doujin instance:
```python
    Doujin(id: str
           title: str
           secondary_title: str
           tags: List[str]
           artists: List[str]
           languages: List[str]
           categories: List[str]
           characters: List[str]
           parodies: List[str]
           groups: List[str]
           images: List[str]
           total_pages: int)
```

It's good always remember that some doujins doesnt have many properties that are listed above like artists, characters, parodies and more. This is only the default Doujin dataclass template.

##### Search

```python
from NHentai.nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    search_obj: SearchPage = nhentai.search(query='naruto', sort='popular', page=1)
    search_obj: SearchPage = nhentai.search(query='30955', sort='popular', page=1)
```

expected output:
```python
    SearchPage(query: str, 
               sort: str, 
               total_results: int, 
               doujins: [DoujinThumbnail(id: str,
                                         title: str, 
                                         lang: str, 
                                         cover: str,
                                         url: str,
                                         data_tags: List[str])], 
               total_pages: int)
```

##### Doujin

```python
from NHentai.nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    doujin: Doujin = nhentai.get_doujin(id='287167')
```

expected output:
```python
    Doujin(id: str
           title: str
           secondary_title: str
           tags: List[str]
           artists: List[str]
           languages: List[str]
           categories: List[str]
           characters: List[str]
           parodies: List[str]
           groups: List[str]
           images: List[str]
           total_pages: int)
```

##### Characters

```python
from NHentai.nhentai import NHentai

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
from NHentai.nhentai import NHentai

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
                                             data_tags: List[str])],
                total_doujins: int)
```

## Introducing NHentai Async
This is the first version of the asynchronous nhentai scrapper. The methods works in the very same way as the base nhentai scrapper, but to make it works you'll have to work with asyncio module using an event loop that you can import from it or get from NHentaiAsync class property: `event_loop`.

Since we're working with async functions, you can only call the NHentaiAsync methods from inside an async funcion or context.

```py
from NHentai.nhentai_async import NHentaiAsync 

if __name__ == '__main__':
    nhentai_async = NHentaiAsync()
    event_loop = nhentai_async.event_loop
    popular = event_loop.run_until_complete(nhentai_async.get_popular_now())
    print(popular)
```

or even

```python
from NHentai.nhentai_async import NHentaiAsync 

nhentai_async = NHentaiAsync()

async def get_popular():
    popular = await nhentai_async.get_popular_now()
    print(popular)

if __name__ == '__main__':
    event_loop = nhentai_async.event_loop
    event_loop.run_until_complete(get_popular())
```