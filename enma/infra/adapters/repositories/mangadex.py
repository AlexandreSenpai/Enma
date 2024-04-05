"""
This module provides an adapter for the mangadex repository.
It contains functions and classes to interact with the mangadex API and retrieve manga data.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union, cast
from urllib.parse import urljoin, urlparse

from requests import Response

import requests

from enma.application.core.handlers.error import (ExceedRateLimit, 
                                                  Forbidden, 
                                                  NotFound, 
                                                  Unknown)
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.utils.logger import logger
from enma.domain.entities.author_page import AuthorPage
from enma.domain.entities.manga import (MIME, 
                                        Chapter, 
                                        Genre, 
                                        Author, 
                                        Image, 
                                        Language, 
                                        Manga, 
                                        SymbolicLink,
                                        Title)
from enma.domain.entities.search_result import Pagination, SearchResult, Thumb
from enma.infra.core.interfaces.mangadex_response import (AuthorRelation, 
                                                          CoverArtRelation, 
                                                          IGetResult, 
                                                          IHash, 
                                                          ISearchResult, 
                                                          IVolumesResponse)


class Sort(Enum):
    ALL_TIME = 'relevance'
    RECENT = 'createdAt'

class Mangadex(IMangaRepository):
    """
    Repository class for interacting with the Mangadex API.
    Provides methods to fetch manga details, search for manga, etc.
    """
    def __init__(self) -> None:
        self.__API_URL = 'https://api.mangadex.org/'
        self.__COVER_URL = 'https://mangadex.org/covers/'
        self.__HASH_URL = 'https://api.mangadex.org/at-home/server/'
        self.__CHAPTER_PAGE_URL = 'https://cmdxd98sb0x3yprd.mangadex.network/data/'

    def __handle_source_response(self, response: Response):
        logger.debug(f'Fetched {response.url} with response status code {response.status_code} and text {response.text}')
        if response.status_code == 200: return
        if response.status_code == 403: 
            raise Forbidden(message='Could not perform a successfull request to the source due credentials issues.\
Check your credentials and try again.')
        if response.status_code == 404:
            raise NotFound(message=f'Could not find the requested resource at "{response.url}". \
Check the provided request parameters and try again.')
        if response.status_code == 429:
            raise ExceedRateLimit(message='You\'ve exceed the mangadex rate limit!')
        raise Unknown(message='Something unexpected happened while trying to fetch source content. \
Set the logging mode to debug and try again.')

    def __make_request(self,
                       url: str,
                       headers: Union[dict[str, Any], None] = None,
                       params: Optional[Union[dict[str, 
                                                   Union[str, int]], 
                                              list[tuple[str, Union[str, int]]]]] = None) -> requests.Response:

        headers = headers if headers is not None else {}
        params = params if params is not None else {}

        logger.debug(f'Fetching {url} with headers {headers} and params {params}')

        response = requests.get(url=urlparse(url).geturl(),
                                headers={**headers, 'User-Agent': 'Enma/2.4.0'},
                                params=params)
        
        self.__handle_source_response(response)

        return response

    def set_config(self, config) -> None:
        raise NotImplementedError('Manganato does not support set config')

    def __create_cover_uri(self, 
                           manga_id: str, 
                           file_name: str) -> str:
        return urljoin(self.__COVER_URL, f'{manga_id}/{file_name}.512.jpg')
    
    def fetch_chapter_by_symbolic_link(self, 
                                       link: SymbolicLink) -> Chapter:

        response = self.__make_request(url=link.link)
        
        ch: IHash = response.json()
        chapter = Chapter()
    
        for index, page in enumerate(ch.get('chapter').get('data')):
            extension = page.split('.')[-1]
            chapter.add_page(Image(uri=self.__create_chapter_page_uri(ch.get('chapter').get('hash'), page),
                                   name=f'{index}.{extension}',
                                   mime=MIME[extension.upper()]))
        return chapter

    def __fetch_chapter_hashes(self, chapter_id: str) -> tuple[str, list[str]]:
        response = self.__make_request(url=urljoin(self.__HASH_URL, chapter_id))
        data: IHash = response.json()

        return (data.get('chapter').get('hash'), 
                data.get('chapter').get('data'))
    
    def __create_chapter_page_uri(self, hash: str, filename: str) -> str:
        return urljoin(self.__CHAPTER_PAGE_URL, f'{hash}/{filename}')

    def __create_chapter(self,
                         chapter: tuple[int, str],
                         with_symbolic_links: bool = False) -> Chapter:
        
        curr_chapter, chapter_id = chapter

        if with_symbolic_links:
            return Chapter(id=curr_chapter, 
                           link=SymbolicLink(link=urljoin(self.__HASH_URL, chapter_id)))
        else:
            ch = Chapter(id=curr_chapter)
            hash, files = self.__fetch_chapter_hashes(chapter_id)
        
            for index, page in enumerate(files):
                extension = page.split('.')[-1]
                ch.add_page(Image(uri=self.__create_chapter_page_uri(hash, page),
                                  name=f'{index}.{extension}',
                                  mime=MIME[extension.upper()]))
        
            return ch
    
    def __list_chapters(self, manga_id: str) -> list[tuple[int, str]]:
        response = self.__make_request(url=urljoin(self.__API_URL, f'manga/{manga_id}/aggregate'))
        
        data: IVolumesResponse = response.json()

        chapters = []
        for volume in data.get('volumes'):
            volume = data.get('volumes').get(volume)
            
            if volume is None: continue

            volume_chapters = volume.get('chapters')
            
            for volume_key in volume_chapters:
                current_vol = volume_chapters.get(volume_key)

                if current_vol is None: continue

                chapters.append((current_vol.get('chapter'), current_vol.get('id')))
        
        return chapters
    
    def get(self, 
            identifier: str,
            with_symbolic_links: bool = False) -> Union[Manga, None]:
        response = self.__make_request(url=urljoin(self.__API_URL, f'manga/{identifier}'),
                                       params=[('includes[]', 'cover_art'),
                                               ('includes[]', 'author'),
                                               ('includes[]', 'artist')])

        result: IGetResult = response.json()
        manga = result.get('data')
        
        authors_data = [relationship for relationship in manga.get('relationships') if relationship.get('type') == 'author']
        authors: list[Author] = []

        if len(authors_data) > 0:
            for author in authors_data:
                author = cast(AuthorRelation, author)
                authors.append(Author(name=author.get('attributes').get('name'),
                                      id=author.get('id')))

        genres = [Genre(id=genre.get('id'),
                        name=genre.get('attributes').get('name').get('en', 'unknown')) for genre in manga.get('attributes').get('tags')]
        
        covers = [tag for tag in manga.get('relationships') if tag.get('type') == 'cover_art']
        cover = cast(CoverArtRelation, covers[0])

        thumbnail = Image(uri=self.__create_cover_uri(manga.get("id"), cover.get("attributes").get("fileName")),
                          width=512)
        
        japanese_title = [ title.get('ja-ro') for title in manga.get('attributes').get('altTitles') if title.get('ja-ro') is not None ][0]

        other_keys = list(manga.get('attributes').get('altTitles')[-1].keys())[0]

        manga = Manga(title=Title(english=manga.get('attributes').get('title').get('en'),
                                  japanese=japanese_title or '',
                                  other=manga.get('attributes').get('altTitles')[-1].get(other_keys) or ''),
                      id=manga.get('id'),
                      created_at=datetime.fromisoformat(manga.get('attributes').get('createdAt')),
                      updated_at=datetime.fromisoformat(manga.get('attributes').get('updatedAt')),
                      language=Language.get(manga.get('attributes').get('originalLanguage').strip().lower().replace('-', '_'), 'unknown'),
                      authors=authors,
                      genres=genres,
                      thumbnail=thumbnail,
                      cover=thumbnail,
                      chapters=[])
        
        chapter_list = self.__list_chapters(manga_id=str(manga.id))

        print(1, chapter_list)

        for chapter in chapter_list:
            manga.add_chapter(self.__create_chapter(chapter=chapter,
                                                    with_symbolic_links=with_symbolic_links))

        return manga
        
    def __make_sort_query(self, sort: Sort) -> dict[str, str]:
        return { f'order[{sort.value if isinstance(sort, Sort) else sort}]': 'desc' }

    def search(self,
               query: str,
               page: int,
               sort: Sort = Sort.RECENT,
               per_page: int = 25) -> SearchResult:
        
        logger.debug(f'Searching into Mangadex with args query={query};page={page};sort={sort}')

        request_response = self.__make_request(url=urljoin(self.__API_URL, 'manga'),
                                               params={'title': query,
                                                       **self.__make_sort_query(sort),
                                                       'includes[]': 'cover_art',
                                                       'limit': per_page,
                                                       'offset': per_page * page if page > 1 else 0})
        
        response: ISearchResult = request_response.json()
        
        search_result = SearchResult(query=query,
                                     total_pages=0,
                                     page=page,
                                     total_results=0,
                                     results=[])
        
        for result in response.get('data', []):
            title = list(result.get('attributes').get('title').values())[0]

            cover_options = [cover_art for cover_art in result.get('relationships') if cover_art.get('type') == 'cover_art']
            cover_url: Union[str, None] = None

            if len(cover_options) > 0:
                cover = cast(CoverArtRelation, cover_options[0])
                cover_url = cover.get('attributes', dict()).get('fileName')

            thumb = Thumb(id=result.get('id'),
                          title=str(title),
                          cover=Image(uri=self.__create_cover_uri(result.get("id"), cover_url or "not-found"),
                                      width=512))
            search_result.results.append(thumb)

        total_results = response.get('total')
        search_result.total_pages = int(total_results / per_page)
        search_result.total_results = total_results

        return search_result

    def paginate(self, page: int) -> Pagination:
        logger.debug(f'Paginating Mangadex with args page={page}')
        per_page = 25
        request_response = self.__make_request(url=urljoin(self.__API_URL, 'manga'),
                                               params=[('limit', per_page),
                                                       ('offset', per_page * (page - 1) if page > 1 else 0),
                                                       ('order[createdAt]', 'desc'),
                                                       ('includes[]', 'cover_art'),
                                                       ('contentRating[]', 'safe'),
                                                       ('contentRating[]', 'suggestive'),
                                                       ('contentRating[]', 'erotica'),
                                                       ('order[createdAt]', 'desc'),
                                                       ('hasAvailableChapters', 'true')])
        
        response: ISearchResult = request_response.json()

        pagination = Pagination(page=page,
                                total_pages=int(response.get('total') / per_page),
                                total_results=response.get('total'),
                                results=[])

        for result in response.get('data', []):
            title = list(result.get('attributes').get('title').values())[0]

            cover_options = [cover_art for cover_art in result.get('relationships') if cover_art.get('type') == 'cover_art']
            cover_url: Union[str, None] = None

            if len(cover_options) > 0:
                cover = cast(CoverArtRelation, cover_options[0])
                cover_url = cover.get('attributes', dict()).get('fileName')

            thumb = Thumb(id=result.get('id'),
                          title=str(title),
                          cover=Image(uri=self.__create_cover_uri(result.get("id"), cover_url or "not_found"),
                                      width=512))
            
            pagination.results.append(thumb)

        return pagination

    def random(self, retry=0) -> Manga:
        response = self.__make_request(url=urljoin(self.__API_URL, f'manga/random'),
                                       params=[('includes[]', 'cover_art'),
                                               ('contentRating[]', 'safe'),
                                               ('contentRating[]', 'suggestive'),
                                               ('contentRating[]', 'erotica'),
                                               ('includes[]', 'author'),
                                               ('includes[]', 'artist')])

        result: IGetResult = response.json()

        manga = result.get('data')
        
        authors_data = [relationship for relationship in manga.get('relationships') if relationship.get('type') == 'author']
        authors: list[Author] = []

        if len(authors_data) > 0:
            for author in authors_data:
                author = cast(AuthorRelation, author)
                authors.append(Author(name=author.get('attributes').get('name'),
                                      id=author.get('id')))

        genres = [Genre(id=genre.get('id'),
                        name=genre.get('attributes').get('name').get('en', 'unknown')) for genre in manga.get('attributes').get('tags')]
        
        covers = [tag for tag in manga.get('relationships') if tag.get('type') == 'cover_art']
        cover = cast(CoverArtRelation, covers[0]) if len(covers) > 0 else None

        thumbnail = Image(uri=self.__create_cover_uri(manga.get("id"), cover.get("attributes").get("fileName")),
                          width=512) if cover is not None else None
        
        japanese_title = [ title.get('ja-ro') or title.get('ja') for title in manga.get('attributes').get('altTitles') if title.get('ja-ro') is not None or title.get('ja') is not None ]
        japanese_title = japanese_title[0] if len(japanese_title) > 0 else None

        other_keys = manga.get('attributes').get('altTitles') if len(manga.get('attributes').get('altTitles')) > 0 else None
        other_keys = list(other_keys[-1].keys() if other_keys is not None else [])
        other_keys = other_keys[0] if len(other_keys) > 0 else None

        other_title = manga.get('attributes').get('altTitles')[-1].get(other_keys, '') if other_keys is not None else ''

        manga = Manga(title=Title(english=manga.get('attributes').get('title').get('en'),
                                  japanese=japanese_title or '',
                                  other=other_title),
                      id=manga.get('id'),
                      created_at=datetime.fromisoformat(manga.get('attributes').get('createdAt')),
                      updated_at=datetime.fromisoformat(manga.get('attributes').get('updatedAt')),
                      language=Language.get(manga.get('attributes').get('originalLanguage').strip().lower().replace('-', '_'), 'unknown'),
                      authors=authors,
                      genres=genres,
                      thumbnail=thumbnail,
                      cover=thumbnail,
                      chapters=[])
        
        chapter_list = self.__list_chapters(manga_id=str(manga.id))

        for chapter in chapter_list:
            manga.add_chapter(self.__create_chapter(chapter=chapter,
                                                    with_symbolic_links=True))

        return manga
    
    def author_page(self,
                    author: str,
                    page: int) -> AuthorPage:
        raise NotImplementedError('Mangadex does not support author page.')