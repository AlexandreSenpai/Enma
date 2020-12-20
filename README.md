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

### Usage

##### Home

```python
from Nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    random_doujin: HomePage = nhentai.get_pages(page=1)
```

the expected output is a HomePage instance:
```python
    HomePage(
        doujins: [
            DoujinThumbnail(
                id: str, 
                title: str, 
                lang: str, 
                cover: str, 
                data_tags: List[str])], 
        total_pages: int)
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
    Doujin(
        id: str
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
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    search_obj: SearchPage = nhentai.search(query='naruto', sort='popular', page=1)
    search_obj: SearchPage = nhentai.search(query='30955', sort='popular', page=1)
```

expected output:
```python
    SearchPage(
        query: str, 
        sort: str, 
        total_results: int, 
        doujins: [
            DoujinThumbnail(
                id: str, 
                title: str, 
                lang: str, 
                cover: str, 
                data_tags: List[str])], 
        total_pages: int)
```

##### Doujin

```python
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    doujin: Doujin = nhentai._get_doujin(id='287167')
```

expected output:
```python
    Doujin(
        id: str
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
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    doujin: Doujin = nhentai.get_characters(page=1)
```

expected output:
```python
    CharacterListPage(
                    page=int,
                    total_pages=int,
                    characters=[
                        CharacterLink(
                            section: str
                            title: str
                            url: str
                            total_entries: int)])
```