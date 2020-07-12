# NHentai API
## An API made using python webscrapping

### Instalation
 pip3 install --upgrade NHentai-API or pip install --upgrade NHentai-API

### Library Features

 - Home page pagination,
 - Doujin information,
 - Random doujin,
 - Search doujin,
 - User favorite page

### Usage

```python
from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    dict: random_doujin = nhentai.get_random()
```
