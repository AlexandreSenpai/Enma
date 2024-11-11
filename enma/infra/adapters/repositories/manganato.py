"""
This module provides an adapter for the MANGANATO repository.
It contains functions and classes to interact with the MANGANATO API and retrieve manga data.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from multiprocessing import cpu_count
import os
from typing import Any, Optional, Union, cast
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Tag

import requests

from enma._version import __version__
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.utils.logger import logger
from enma.domain.entities.author_page import AuthorPage
from enma.domain.entities.manga import Author, Chapter, Genre, Image, Manga, SymbolicLink, Title
from enma.domain.entities.search_result import Pagination, SearchResult, Thumb
from enma.infra.core.utils.cache import Cache

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
                       headers: Union[dict[str, Any], None] = None,
                       params: Optional[dict[str, Union[str, int]]] = None):

        headers = headers if headers is not None else {}
        params = params if params is not None else {}

        logger.debug(f'Fetching {url} with headers {headers} and params {params}')

        return requests.get(url=urlparse(url).geturl(), 
                            headers={**headers, 
                                     'Referer': 'https://chapmanganato.com/', 
                                     "User-Agent": f"Enma/{__version__}"},
                            params={**params})
    
    def __create_title(self, 
                       main_title: str, 
                       alternative: str) -> Title:
        logger.debug(f'Building manga title main: {main_title} and alternative: {alternative}')

        has_many_alternatives = alternative.find(';') != -1 or alternative.find(',') != -1

        if not has_many_alternatives:
            jp = alternative
            return Title(english=main_title.strip(),
                         japanese=jp.strip(),
                         other=main_title.strip())

        jp, cn, *_ = alternative.split(';') if alternative.find(';') != -1 else alternative.split(',')
        return Title(english=main_title.strip(),
                     japanese=jp.strip(),
                     other=cn.strip())
    
    def __find_chapters_list(self, html: BeautifulSoup) -> list[str]:
        chapter_list = cast(Tag, html.find('ul', {'class': 'row-content-chapter'}))
        chapters = chapter_list.find_all('li') if chapter_list else []
        return [chapter.find('a')['href'] for chapter in chapters]
    
    def __create_chapter(self, url: str, symbolic: bool = False) -> Union[Chapter, None]:

        if symbolic:
            return Chapter(id=url.split('/')[-1], link=SymbolicLink(link=url))

        response = self.__make_request(url=url)
        logger.debug(f'Fetching chapter {url}')
        
        if response.status_code != 200:
            logger.error(f'Could not fetch the chapter with url: {url}. status code: {response.status_code}')
            return
        
        chapter = Chapter(id=response.url.split('/')[-1])
        html = BeautifulSoup(response.text, 'html.parser')
        images_container = cast(Tag, html.find('div', {'class': 'container-chapter-reader'}))

        for img in images_container.find_all('img'):
            chapter.add_page(Image(uri=img['src'],
                                   name=img['src'].split('/')[-1],
                                   width=0,
                                   height=0))
        return chapter
    
    def set_config(self, **kwargs) -> None:
        raise NotImplementedError('Manganato does not support set_config')

    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_GET_TTL_IN_SECONDS', 300)), 
           max_size=20).cache
    def get(self, 
            identifier: str,
            with_symbolic_links: bool = False) -> Union[Manga, None]:
        response = self.__make_request(url=urljoin(self.__CHAPTER_BASE_URL, identifier))
        
        if response.status_code != 200:
            logger.error(f'Could not fetch the manga with identifier: {identifier}. status code: {response.status_code}')
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

        if title_div is None: return

        h1_elem = title_div.find('h1')
        h1_tag = cast(Tag, h1_elem)
        h1_text = h1_tag.text if h1_elem is not None else ''
        elem_title = h1_text
    
        table = cast(Tag, soup.find('table', {'class': 'variations-tableInfo'}))
        
        if table is None: return

        table_vals = table.find_all('td', {'class': 'table-value'})
        
        if table_vals is None: return
        
        title_cel, author_cel, status_cel, genres_cel = table_vals
        title = self.__create_title(main_title=elem_title, 
                                    alternative=title_cel.text)
        author = author_cel.text.strip()
        status = status_cel.text.strip().lower()
  
        genres = genres_cel.text.replace('\n', '').split(' - ')

        extra_infos = cast(Tag, soup.find('div', {'class': 'story-info-right-extent'}))

        updated_at = None
        if extra_infos:
            updated_at_field = extra_infos.find_all('p')[0]
            updated_at = updated_at_field.find('span', {'class': 'stre-value'}).text

        if with_symbolic_links:
            chapters_links = self.__find_chapters_list(html=soup)
            chapters = [self.__create_chapter(link, symbolic=True) for link in chapters_links]
        else:
            workers = cpu_count()
            logger.debug(f'Initializing {workers} workers to fetch chapters of {identifier}.')

            with ThreadPoolExecutor(max_workers=workers) as executor:
                chapters = executor.map(self.__create_chapter, self.__find_chapters_list(html=soup))
                chapters = list(filter(lambda x: isinstance(x, Chapter), list(chapters)))
                executor.shutdown()
        
        return Manga(title=title,
                     status='completed' if status == 'completed' else 'ongoing',
                     authors=[Author(name=author)] if author is not None else None,
                     genres=[Genre(name=genre_name) for genre_name in genres],
                     url=urljoin(self.__BASE_URL, identifier),
                     id=identifier,
                     created_at=datetime.strptime(updated_at, "%b %d,%Y - %H:%M %p") if updated_at else None,
                     updated_at=datetime.strptime(updated_at, "%b %d,%Y - %H:%M %p") if updated_at else None,
                     thumbnail=Image(uri=cover), # type: ignore
                     cover=Image(uri=cover), # type: ignore
                     chapters=chapters) # type: ignore
    
    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_SEARCH_TTL_IN_SECONDS', 100)), 
           max_size=5).cache
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
                                url=result.find('a', {'class': 'a-h text-nowrap item-title'})['href'],
                                cover=Image(uri=result.find('img')['src'], width=0, height=0),
                                id=result.find('a', {'class': 'a-h text-nowrap item-title'})['href'].split('/')[-1]))

        return SearchResult(query=query,
                            page=page,
                            total_pages=total_pages,
                            results=thumbs)

    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_PAGINATE_TTL_IN_SECONDS', 100)), 
           max_size=5).cache
    def paginate(self, page: int) -> Pagination:
        response = self.__make_request(url=f'{self.__BASE_URL}/genre-all/{page}')
        
        pagination = Pagination(page=page)

        if response.status_code != 200:
            return pagination
        
        soup = BeautifulSoup(response.text, 'html.parser')

        content_panel = soup.find('div', {'class': 'panel-content-genres'})
        
        if content_panel is None:
            return pagination
        
        content_panel = cast(Tag, content_panel)
        content_items = content_panel.find_all('div', {'class': 'content-genres-item'})
        
        for item in content_items:
            item = cast(Tag, item)
            info = cast(Tag, item.find('a', {'class': 'genres-item-img bookmark_check'}))
            cover = info.find('img')
            pagination.results.append(Thumb(id=info['href'].split('/')[-1], # type: ignore
                                            url=info['href'], # type: ignore
                                            title=info['title'] if info is not None else "", # type: ignore
                                            cover=Image(uri=cover['src'], width=0, height=0))) # type: ignore
            
        last_pagination = soup.find('a', {'class': 'page-blue page-last'})
        pagination.total_pages = int(last_pagination['href'].split('/')[-1]) # type: ignore
        pagination.total_results = 24 * int(pagination.total_pages)
        
        return pagination
    
    def random(self) -> Manga:
        raise NotImplementedError('Manganato does not support random')
    
    def author_page(self, author: str, page: int) -> AuthorPage:
        raise NotImplementedError('Manganato does not support author_page')
    
    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_FETCH_SYMBOLIC_LINK_TTL_IN_SECONDS', 100)), 
           max_size=20).cache
    def fetch_chapter_by_symbolic_link(self, link: SymbolicLink) -> Chapter:
        chapter =  self.__create_chapter(url=link.link)
        
        if chapter is not None:
            return chapter
        
        return Chapter(id=0)
