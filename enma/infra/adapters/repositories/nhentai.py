"""
This module provides an adapter for the nhentai repository.
It contains functions and classes to interact with the nhentai API and retrieve manga data.
"""
from datetime import datetime, timezone
from enum import Enum
import os
from typing import Any, List, Literal, Optional, Union, cast
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, field_validator

import requests
from bs4 import BeautifulSoup, Tag

from enma.application.core.handlers.error import (ExceedRetryCount, Forbidden, InvalidConfig, InvalidRequest,
                                                  NotFound, Unknown)
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.utils.logger import logger
from enma.domain.entities.author_page import AuthorPage
from enma.domain.entities.manga import (MIME, Chapter, Genre, Author, Image, Manga, SymbolicLink,
                                        Title, Tag as EnmaTag)
from enma.domain.entities.search_result import Pagination, SearchResult, Thumb
from enma.domain.utils import mime
from enma.infra.core.interfaces.nhentai_response import NHentaiImage, NHentaiResponse, Tag as NHentaiResponseTag
from enma.infra.core.utils.cache import Cache
from enma._version import __version__


class CloudFlareConfig(BaseModel):
    user_agent: str
    cf_clearance: str

    @field_validator('user_agent')
    def user_agent_validator(cls, value: str) -> str:
        if value == '': raise InvalidRequest(message='User Agent cant be empty.')
        return str(value)

    @field_validator('cf_clearance')
    def cf_clearance_validator(cls, value: str) -> str:
        if value == '': raise InvalidRequest(message='CF Clearance cant be empty.')
        return str(value)

class __StrEnum(str, Enum):...

class Sort(__StrEnum):
    TODAY = 'popular-today'
    WEEK = 'popular-week'
    ALL_TIME = 'popular'
    RECENT = None

TagType = Union[Literal["language"],
                Literal["parody"],
                Literal["character"],
                Literal["group"],
                Literal["artist"],
                Literal["tag"],
                Literal["category"]]

class NHentai(IMangaRepository):
    """
    Repository class for interacting with the nhentai API.
    Provides methods to fetch manga details, search for manga, etc.
    """
    def __init__(self,
                 config: Optional[CloudFlareConfig] = None) -> None:
        self.__config = config
        self.__BASE_URL = 'https://nhentai.net/'
        self.__API_URL = 'https://nhentai.net/api/'
        self.__IMAGE_BASE_URL = 'https://i.nhentai.net/galleries/'
        self.__AVATAR_URL = 'https://i5.nhentai.net/'
        self.__TINY_IMAGE_BASE_URL = self.__IMAGE_BASE_URL.replace('/i.', '/t.')

    def __handle_source_response(self, response: requests.Response):
        logger.debug(f'Fetched {response.url} with response status code {response.status_code} and text {response.text}')
        if response.status_code == 200: return
        if response.status_code == 403: 
            raise Forbidden(message='Could not perform a successfull request to the source due credentials issues. \
Check your credentials and try again.')
        if response.status_code == 404:
            raise NotFound(message=f'Could not find the requested resource at "{response.url}". \
Check the provided request parameters and try again.')
        raise Unknown(message='Something unexpected happened while trying to fetch source content. \
Set the logging mode to debug and try again.')

    def __make_request(self,
                       url: str,
                       headers: Union[dict[str, Any], None] = None,
                       params: Optional[dict[str, Union[str, int]]] = None) -> requests.Response:

        headers = headers if headers is not None else {}
        params = params if params is not None else {}

        config = self.__config
        user_agent = config.user_agent if config is not None else f"Enma/{__version__}"
        cookies = {'cf_clearance': config.cf_clearance} if config is not None else {}

        logger.debug(f'Fetching {url} with headers {headers}, params {params} and cookies: {cookies}')

        response = requests.get(url=urlparse(url).geturl(),
                                headers={**headers, 'User-Agent': user_agent},
                                params={**params},
                                cookies=cookies)
        
        self.__handle_source_response(response)

        return response

    def set_config(self, config: CloudFlareConfig) -> None:
        if not isinstance(config, CloudFlareConfig): raise InvalidConfig(message='You must provide a CloudFlareConfig object.') 
        self.__config = config
    
    def __make_page_uri(self,
                        type: Union[Literal['cover'], Literal['page'], Literal['thumbnail']],
                        media_id: str,
                        mime: MIME,
                        page_number: Optional[int] = None) -> str:
        
        url = ''

        # cannot use switch case because this lib intends to support python 3.9+
        if type == 'cover': 
            url = urljoin(self.__TINY_IMAGE_BASE_URL, f'{media_id}/cover.{mime.value}')
        elif type == 'thumbnail': 
            url = urljoin(self.__TINY_IMAGE_BASE_URL, f'{media_id}/thumb.{mime.value}')
        else:
            url = urljoin(self.__IMAGE_BASE_URL, f'{media_id}/{page_number}.{mime.value}')
        
        logger.debug(f'Built page uri for type {type} as {url}')

        return url
    
    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_FETCH_SYMBOLIC_LINK_TTL_IN_SECONDS', 100)), 
           max_size=20).cache
    def fetch_chapter_by_symbolic_link(self, 
                                       link: SymbolicLink) -> Chapter:
        response = self.__make_request(url=link.link)
        
        doujin: NHentaiResponse = response.json()

        if doujin.get('media_id') is None or doujin.get('images') is None:
            return Chapter()

        return self.__create_chapter(url=link.link, 
                                     with_symbolic_links=False, 
                                     media_id=doujin.get('media_id'), 
                                     pages=doujin.get('images').get('pages'))

    def __create_chapter(self,
                         url: str,
                         media_id: str, 
                         pages: list[NHentaiImage],
                         with_symbolic_links: bool = False) -> Chapter:
        
        if with_symbolic_links:
            return Chapter(link=SymbolicLink(link=url))
        else:
            chapter = Chapter()
            for index, page in enumerate(pages):
                safe_mime = mime.get_mime_safelly(page.get('t').upper())

                if safe_mime is None:
                    logger.warning(f'Could not find a valid mime type for page {index+1}. Forcing mime type as JPG.')

                safe_mime = safe_mime if safe_mime is not None else MIME.J

                chapter.add_page(Image(uri=self.__make_page_uri(type='page',
                                                                mime=safe_mime,
                                                                media_id=media_id,
                                                                page_number=index+1),
                                name=f'{index}.{safe_mime.value}',
                                mime=safe_mime,
                                width=page.get('w'),
                                height=page.get('h')))
            return chapter
        
    def __get_tag_by_type(self, 
                          type: TagType, 
                          tags: List[NHentaiResponseTag]) -> List[NHentaiResponseTag]:
        return list(filter(lambda tag: tag.get('type') == type, tags))
    
    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_GET_TTL_IN_SECONDS', 300)), 
           max_size=20).cache
    def get(self, 
            identifier: str,
            with_symbolic_links: bool = False) -> Union[Manga, None]:

        url = urljoin(self.__API_URL, f'gallery/{identifier}')
        response = self.__make_request(url=url)

        doujin: NHentaiResponse = response.json()
        media_id = doujin.get('media_id')

        nhentai_tags = doujin.get('tags')

        chapter = self.__create_chapter(url=url,
                                        with_symbolic_links=with_symbolic_links,
                                        media_id=media_id, 
                                        pages=doujin.get('images').get('pages'))

        language = [tag.get('name') 
                    for tag in self.__get_tag_by_type(type='language',
                                                      tags=nhentai_tags)]
        
        authors = [Author(id=tag.get('id'),
                          name=tag.get('name')) 
                    for tag in self.__get_tag_by_type(type='artist',
                                                      tags=nhentai_tags)]
        
        genres = [Genre(id=tag.get('id'),
                        name=tag.get('name')) 
                    for tag in self.__get_tag_by_type(type='tag',
                                                      tags=nhentai_tags)]
        
        characters = [EnmaTag(type='character',
                              name=tag.get('name'),
                              id=tag.get('id')) 
                      for tag in self.__get_tag_by_type(type='character',
                                                        tags=nhentai_tags)]
        
        related = [EnmaTag(type='related',
                           name=tag.get('name'),
                           id=tag.get('id')) 
                      for tag in self.__get_tag_by_type(type='parody',
                                                        tags=nhentai_tags)]
        
        category = [EnmaTag(type='category',
                            name=tag.get('name'),
                            id=tag.get('id')) 
                      for tag in self.__get_tag_by_type(type='category',
                                                        tags=nhentai_tags)]
        
        tags = [*characters, *related, *category]
        
        safe_mime = mime.get_mime_safelly(doujin.get('images').get('thumbnail').get('t').upper())
        safe_mime = safe_mime if safe_mime is not None else MIME.J

        thumbnail = Image(uri=self.__make_page_uri(type='thumbnail',
                                                   mime=safe_mime,
                                                   media_id=media_id),
                          mime=safe_mime,
                          width=doujin.get("images").get("thumbnail").get("w"),
                          height=doujin.get("images").get("thumbnail").get("h"))
        
        safe_mime = mime.get_mime_safelly(doujin.get("images").get("cover").get("t").upper())
        safe_mime = safe_mime if safe_mime is not None else MIME.J

        cover = Image(uri=self.__make_page_uri(type='cover',
                                               media_id=media_id,
                                               mime=safe_mime),
                      mime=safe_mime,
                      width=doujin.get("images").get("cover").get("w"),
                      height=doujin.get("images").get("cover").get("h"))

        manga = Manga(title=Title(english=doujin.get('title').get('english'),
                                  japanese=doujin.get('title').get('japanese'),
                                  other=doujin.get('title').get('pretty')),
                      id=doujin.get('id'),
                      created_at=datetime.fromtimestamp(doujin.get('upload_date'), tz=timezone.utc),
                      updated_at=datetime.fromtimestamp(doujin.get('upload_date'), tz=timezone.utc),
                      status='completed',
                      url=urljoin(self.__BASE_URL, f'g/{doujin.get("id")}'),
                      language=language[0] if len(language) > 0 else None,
                      authors=authors,
                      genres=genres,
                      thumbnail=thumbnail,
                      tags=tags,
                      cover=cover,
                      chapters=[chapter])

        return manga
    
    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_SEARCH_TTL_IN_SECONDS', 100)), 
           max_size=5).cache
    def search(self,
               query: str,
               page: int,
               sort: Sort = Sort.RECENT) -> SearchResult:
        
        logger.debug(f'Searching into Nhentai with args query={query};page={page};sort={sort}')

        request_response = self.__make_request(url=urljoin(self.__BASE_URL, 'search'),
                                               params={'q': query,
                                                       'sort': sort if isinstance(sort, str) else sort.value,
                                                       'page': page})
        
        search_result = SearchResult(query=query,
                                     total_pages=0,
                                     page=page,
                                     total_results=0,
                                     results=[])
        
        soup = BeautifulSoup(request_response.text, 'html.parser')

        search_results_container = soup.find('div', {'class': 'container'})
        logger.debug(f'Found successfully search result container using .class.container.')
        pagination_container = soup.find('section', {'class': 'pagination'})
        logger.debug(f'Found successfully pagination container using .class.pagination.')

        last_page_a_tag = pagination_container.find('a', {'class': 'last'}) if pagination_container else None # type: ignore
        logger.debug(f'Found last pagination container using .calss.last.')
        total_pages = int(last_page_a_tag['href'].split('=')[-1]) if last_page_a_tag else 1 # type: ignore
        logger.debug(f'Found last page number successfully splitting last pagination number href.')

        if not search_results_container:
            return search_result

        search_results = search_results_container.find_all('div', {'class': 'gallery'}) # type: ignore
        logger.debug(f'Found search results container using .class.gallery')
        
        if not search_results:
            return search_result
        
        a_tags_with_doujin_id = [gallery.find('a', {'class': 'cover'}) for gallery in search_results]

        thumbs = []

        for a_tag in a_tags_with_doujin_id:
            if a_tag is None: continue

            doujin_id = a_tag['href'].split('/')[-2]

            if doujin_id == '': continue

            result_cover = a_tag.find('img', {'class': 'lazyload'})
            cover_uri = None
            width = None
            height = None

            if result_cover is not None:
                cover_uri = result_cover['data-src']
                width = result_cover['width']
                height = result_cover['height']

            result_caption = a_tag.find('div', {'class': 'caption'})

            caption = None
            if result_caption is not None:
                caption = result_caption.text

            thumbs.append(Thumb(id=doujin_id,
                                url=urljoin(self.__BASE_URL, f'g/{doujin_id}'),
                                cover=Image(uri=cover_uri or '',
                                            mime=MIME.J,
                                            width=int(width or 0),
                                            height=int(height or 0)),
                                title=caption or ''))

        search_result.total_pages = total_pages
        search_result.total_results = 25 * total_pages if pagination_container else len(thumbs)
        search_result.results = thumbs

        return search_result

    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_PAGINATE_TTL_IN_SECONDS', 100)), 
           max_size=5).cache
    def paginate(self, page: int) -> Pagination:
        response = self.__make_request(url=urljoin(self.__API_URL, f'galleries/all'),
                                       params={'page': page})

        data = response.json()

        PAGES = data.get('num_pages', 0)
        PER_PAGE = data.get('per_page', 0)
        TOTAL_RESULTS = int(PAGES) * int(PER_PAGE)


        
        pagination = Pagination(page=int(page),
                                total_results=TOTAL_RESULTS,
                                total_pages=PAGES,
                                results=[])
        
        for result in data.get('result'):
            safe_mime = mime.get_mime_safelly(result.get('images').get('cover').get('t').upper())
            safe_mime = safe_mime if safe_mime is not None else MIME.J
            thumb = Thumb(
                id=result.get('id'),
                title=result.get('title').get('english'),
                url=urljoin(self.__BASE_URL, f'g/{result.get("id")}'),
                cover=Image(
                    uri=self.__make_page_uri(
                        type='cover',
                        media_id=result.get('media_id'),
                        mime=safe_mime
                    ),
                    mime=safe_mime,
                    width=result.get('images').get('cover').get('w'),
                    height=result.get('images').get('cover').get('h')
                )
            )

            pagination.add_result(thumb)

        return pagination

    def random(self, retry=0) -> Manga:
        response = self.__make_request(url=urljoin(self.__BASE_URL, 'random'))

        soup = BeautifulSoup(response.text, 'html.parser')

        id = cast(Tag, soup.find('h3', id='gallery_id')).text.replace('#', '')
        logger.debug(f'Got successfully random manga id {id} from "gallery_id.h3" tag.')
        logger.debug(f'Using get method to Fetch manga with identifier: {id}')
        doujin = self.get(identifier=id)
        logger.debug(f'Got successfully random manga with id {id}.')

        if doujin is None:
            if retry >= 4:
                raise ExceedRetryCount('Could not fetch a random doujin after 4 retries.')
            
            logger.warning('Could not fetch random manga. Retrying.')
            return self.random(retry=retry+1)

        return doujin
    
    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_AUTHOR_TTL_IN_SECONDS', 100)), 
           max_size=5).cache
    def author_page(self,
                    author: str,
                    page: int) -> AuthorPage:
        request_response = self.__make_request(url=urljoin(self.__BASE_URL, f'artist/{author}'),
                                               params={'page': page})
        
        result = AuthorPage(author=author,
                            total_pages=0,
                            page=page,
                            total_results=0,
                            results=[]) 
   
        soup = BeautifulSoup(request_response.text, 'html.parser')

        search_results_container = soup.find('div', {'class': 'container'})
        pagination_container = soup.find('section', {'class': 'pagination'})

        last_page_a_tag = pagination_container.find('a',
                                                    {'class': 'last'}) if pagination_container else None  # type: ignore
        total_pages = int(last_page_a_tag['href'].split('=')[-1]) if last_page_a_tag else 1  # type: ignore

        if not search_results_container:
            return result

        search_results = search_results_container.find_all('div', {'class': 'gallery'})  # type: ignore

        if not search_results:
            return result

        a_tags_with_doujin_id = [gallery.find('a', {'class': 'cover'}) for gallery in search_results]

        thumbs = []

        for a_tag in a_tags_with_doujin_id:
            if a_tag is None: continue

            doujin_id = a_tag['href'].split('/')[-2]

            if doujin_id == '': continue

            result_cover = a_tag.find('img', {'class': 'lazyload'})
            cover_uri = None
            width = None
            height = None

            if result_cover is not None:
                cover_uri = result_cover['data-src']
                width = result_cover['width']
                height = result_cover['height']

            result_caption = a_tag.find('div', {'class': 'caption'})

            caption = None
            if result_caption is not None:
                caption = result_caption.text

            thumbs.append(Thumb(id=doujin_id,
                                url=urljoin(self.__BASE_URL, f'g/{doujin_id}'),
                                cover=Image(uri=cover_uri or '',
                                            mime=MIME.J,
                                            width=int(width or 0),
                                            height=int(height or 0)),
                                title=caption or ''))
        
        result.author = author
        result.total_pages = total_pages
        result.page = page
        result.total_results = 25 * total_pages if pagination_container else len(thumbs)
        result.results = thumbs
        
        return result
