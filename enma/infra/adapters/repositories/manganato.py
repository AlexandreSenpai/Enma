"""
This module provides an adapter for the nhentai repository.
It contains functions and classes to interact with the nhentai API and retrieve manga data.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, cast
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Tag

import requests

from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.domain.entities.manga import Chapter, Image, Manga, Title
from enma.domain.entities.search_result import Pagination, SearchResult, Thumb

class Manganato(IMangaRepository):
    """
    Repository class for interacting with the Manganato website.
    Provides methods to fetch manga details, search for manga, etc.
    """
    def __init__(self) -> None:
        self.__BASE_URL = 'https://manganato.com'
        self.__CHAPTER_BASE_URL = 'https://chapmanganato.com'

    def __make_request(self, 
                       url: str,
                       headers: dict[str, Any] | None = None,
                       params: Optional[dict[str, str | int]] = None):

        headers = headers if headers is not None else {}
        params = params if params is not None else {}

        return requests.get(url=urlparse(url).geturl(), 
                            headers={**headers, 'Referer': 'https://chapmanganato.com/'},
                            params={**params})
    
    def __create_title(self, 
                       main_title: str, 
                       alternative: str) -> Title:
        jp, cn, *_ = alternative.split(';') if alternative.find(';') != -1 else alternative.split(',')
        return Title(english=main_title.strip(),
                     japanese=jp.strip(),
                     other=cn.strip())
    
    def __find_chapets_list(self, html: BeautifulSoup) -> list[str]:
        chapter_list = cast(Tag, html.find('ul', {'class': 'row-content-chapter'}))
        chapters = chapter_list.find_all('li') if chapter_list else []
        return [chapter.find('a')['href'] for chapter in chapters]
    
    def __create_chapter(self, url: str) -> Chapter | None:
        response = self.__make_request(url=url)
        
        if response.status_code != 200:
            return
        
        chapter = Chapter(id=response.url.split('/')[-1])
        html = BeautifulSoup(response.text, 'html.parser')
        images_container = cast(Tag, html.find('div'))
        chapter.pages = [Image(uri=img['src'],
                               width=0,
                               height=0) for img in images_container.find_all('img')]
        return chapter

    def get(self, identifier: str) -> Manga | None:
        response = self.__make_request(url=urljoin(self.__CHAPTER_BASE_URL, identifier))
        
        if response.status_code != 200:
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')

        title: Title = Title()
        author: Optional[str] = None
        genres: list[str] = []
        cover = None

        elem_title = ''

        cover_img = cast(Tag, soup.find('span', {'class': 'info-image'}))
        if cover_img: 
            cover_tag = cast(Tag, cover_img.find('img'))
            if cover_tag:
                cover = cover_tag['src']

        title_div = soup.find('div', {'class': 'story-info-right'})
        if title_div is not None:
            h1_elem = title_div.find('h1')
            h1_tag = cast(Tag, h1_elem)
            h1_text = h1_tag.text if h1_elem is not None else ''
            elem_title = h1_text
        
        table = cast(Tag, soup.find('table', {'class': 'variations-tableInfo'}))
        table_vals = table.find_all('td', {'class': 'table-value'})
        
        if table_vals:
            title_cel, author_cel, _, genres_cel = table_vals
            title = self.__create_title(main_title=elem_title, 
                                        alternative=title_cel.text)
            author = author_cel.text.strip()
            genres = genres_cel.text.replace('\n', '').split(' - ')

        with ThreadPoolExecutor(max_workers=10) as executor:
            chapters = executor.map(self.__create_chapter, self.__find_chapets_list(html=soup))
            chapters = list(filter(lambda x: isinstance(x, Chapter), list(chapters)))
        
        return Manga(title=title,
                     author=author,
                     genres=genres,
                     id=identifier,
                     thumbnail=None,
                     cover=cover, # type: ignore
                     chapters=cast(list[Chapter], chapters))
    
    def search(self, 
               query: str,
               page: int) -> SearchResult:
        
        response = self.__make_request(url=urljoin(f'{self.__BASE_URL}/search/story/', "_".join(query.split())),
                                       params={'page': page})
        
        if response.status_code != 200:
            return SearchResult(query=query,
                                page=page)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        total_pages = 0
        total_pages_elem = soup.find('a', {'class': 'page-blue page-last'})
        if total_pages_elem:
            total_pages = int(total_pages_elem['href'].split('page=')[-1]) # type: ignore

        results = soup.find_all('div', {'class': 'search-story-item'})

        thumbs: list[Thumb] = []

        for result in results:
            thumbs.append(Thumb(title=result.find('h3').text.replace('\n', '').strip(),
                                cover=Image(uri=result.find('img')['src'], width=0, height=0),
                                id=result.find('a', {'class': 'a-h text-nowrap item-title'})['href'].split('/')[-1]))

        return SearchResult(query=query,
                            page=page,
                            total_pages=total_pages,
                            results=thumbs)

    def paginate(self, page: int) -> Pagination:
        return super().paginate(page)
    
    def random(self) -> Manga:
        return super().random()