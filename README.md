# NHentai API
A NHentai API made using python webscrapping
For update notes follow me on [Twitter](https://twitter.com/AlexandreSenpa1).

### Instalation
 pip3 install --upgrade NHentai-API or pip install --upgrade NHentai-API

### Library Features

<<<<<<< HEAD
- Home page pagination,
- Doujin information,
- Random doujin,
- Search by id and tag,
- User page
=======
 - Home page pagination,
 - Doujin information,
 - Random doujin,
 - Search doujin,
 - User favorite page
>>>>>>> 97670f916445236286fab42953aed89b4ec5e182

### Usage

##### Home

```python
from nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    random_doujin: dict = nhentai.get_pages(page=1)
```

expected output:
```python
    {
        'doujins': [{
            'id': str, 
            'title': str, 
            'lang': str, 
            'cover': str, 
            'data-tags': list[str]
        }], 
        'totalPages': int
    }
```

##### Random

```python
from nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    random_doujin: dict = nhentai.get_random()
```

expected output:
```python
    {
        'id': str, 
        'title': str, 
        'secondary_title': str, 
        'tags': list[str], 
        'artists': list[str], 
        'languages': list[str], 
        'categories': list[str], 
        'pages': list[str], 
        'images': list[str]
    }
```

##### Search

```python
from nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    search_obj: dict = nhentai.search(query='naruto', sort='popular', page=1)
    search_obj: dict = nhentai.search(query='30955', sort='popular', page=1)
```

expected output:
```python
    {
        'query': str, 
        'sort': str, 
        'totalResults': int, 
        'doujins': [{
            'id': str, 
            'title': str', 
            'lang': str, 
            'cover': str, 
            'data-tags': list[str]
        }], 
        'totalPages': int
    }
```

##### User page

```python
from nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    user: dict = nhentai.get_user_page(uid='1278294', username='alexandresenpai')
```

expected output:
```python
    {
        'uid': str, 
        'username': str, 
        'image': str, 
        'since': str, 
        'doujins': [{
            'id': str, 
            'cover': str, 
            'title': str, 
            'data-tags': list[str]
        }]
    }
```

##### Doujin

```python
from nhentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    doujin: dict = nhentai._get_doujin(id='287167')
```

expected output:
```python
    {
        'id': str, 
        'title': str, 
        'secondary_title': str, 
        'tags': list[str], 
        'artists': list[str], 
        'languages': list[str], 
        'categories': list[str], 
        'pages': list[str], 
        'images': list[str]
    }
```