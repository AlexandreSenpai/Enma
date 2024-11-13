"""
This module provides an adapter for the mangadex repository.
It contains functions and classes to interact with the mangadex API and retrieve manga data.
"""
from datetime import datetime
from enum import Enum
import os
from typing import Any, Optional, Union, cast
from urllib.parse import urljoin, urlparse

import requests

from enma._version import __version__
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
from enma.domain.utils import mime
from enma.infra.core.interfaces.mangadex_response import (AuthorRelation, 
                                                          CoverArtRelation, IAltTitles, 
                                                          IGetResult, 
                                                          IHash, IManga, IMangaTag, IRelations, 
                                                          ISearchResult, 
                                                          IVolumesResponse)
from enma.infra.core.utils.cache import Cache


class Sort(Enum):
    ALL_TIME = 'relevance'
    RECENT = 'createdAt'

class Mangadex(IMangaRepository):
    """
    Repository class for interacting with the Mangadex API.
    Provides methods to fetch manga details, search for manga, etc.
    """

    def __init__(self) -> None:
        self.__SITE_URL = 'https://mangadex.org/'
        self.__API_URL = 'https://api.mangadex.org/'
        self.__COVER_URL = 'https://mangadex.org/covers/'
        self.__HASH_URL = 'https://api.mangadex.org/at-home/server/'
        self.__CHAPTER_PAGE_URL = 'https://cmdxd98sb0x3yprd.mangadex.network/data/'

    def __handle_source_response(self, response: requests.Response):
        """
        Evaluates the HTTP response from the Mangadex API, raising specific exceptions based on the HTTP status code
        to indicate various error conditions such as rate limits exceeded, forbidden access, or resource not found.

        Args:
            response (Response): The HTTP response object from a request to the Mangadex API.

        Raises:
            Forbidden: Indicates a 403 Forbidden HTTP status code.
            NotFound: Indicates a 404 Not Found HTTP status code.
            ExceedRateLimit: Indicates a 429 Too Many Requests HTTP status code.
            Unknown: Indicates any other unexpected HTTP status code.
        """

        logger.debug(f'Fetched {response.url} with response status code {response.status_code} and text {response.text}')

        if response.status_code == 200:
            return
        if response.status_code == 403:
            raise Forbidden(message='Could not perform a successful request to the source due to credentials issues. Check your credentials and try again.')
        if response.status_code == 404:
            raise NotFound(message=f'Could not find the requested resource at "{response.url}". Check the provided request parameters and try again.')
        if response.status_code == 429:
            raise ExceedRateLimit(message='You have exceeded the Mangadex rate limit!')
        raise Unknown(message='Something unexpected happened while trying to fetch source content. Set the logging mode to debug and try again.')

    def __make_request(self,
                       url: str,
                       headers: Union[dict[str, Any], None] = None,
                       params: Optional[Union[dict[str, Union[str, int]], list[tuple[str, Union[str, int]]]]] = None) -> requests.Response:
        """
        Makes a request to the specified URL with the given headers and parameters.

        Args:
            url (str): The URL to make the request to.
            headers (dict[str, Any], optional): The headers to include in the request. Defaults to None.
            params (Optional[Union[dict[str, Union[str, int]], list[tuple[str, Union[str, int]]]]], optional): The parameters to include in the request. Defaults to None.

        Returns:
            requests.Response: The response object from the API request.
        """
        headers = headers if headers is not None else {}
        params = params if params is not None else {}

        logger.debug(f'Fetching {url} with headers {headers} and params {params}')

        response = requests.get(url=urlparse(url).geturl(),
                                headers={**headers, "User-Agent": f"Enma/{__version__}"},
                                params=params)
        
        self.__handle_source_response(response)

        return response

    def set_config(self, config) -> None:
        raise NotImplementedError('Manganato does not support set config')

    def __create_cover_uri(self, 
                           manga_id: str, 
                           file_name: str) -> str:
        """
        Constructs a URL for a manga's cover image based on its identifier and the file name of the cover image.

        Args:
            manga_id (str): The unique identifier of the manga.
            file_name (str): The file name of the cover image.

        Returns:
            str: The fully qualified URL to the cover image.
        """
        return urljoin(self.__COVER_URL, f'{manga_id}/{file_name}.512.jpg')
    
    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_FETCH_SYMBOLIC_LINK_TTL_IN_SECONDS', 100)), 
           max_size=20).cache
    def fetch_chapter_by_symbolic_link(self, 
                                       link: SymbolicLink) -> Chapter:
        """
        Retrieves manga chapter details including pages and images by following a symbolic link. This method is particularly
        useful for fetching chapters that have been directly linked.

        Args:
            link (SymbolicLink): An object representing the symbolic link to the chapter.

        Returns:
            Chapter: An object containing the fetched chapter details such as pages and images.
        """
        response = self.__make_request(url=link.link)
        
        ch: IHash = response.json()
        chapter = Chapter()

    
        for index, page in enumerate(ch.get('chapter').get('data')):
            extension = page.split('.')[-1]
            safe_mime = mime.get_mime_safelly(extension.upper())
            
            if safe_mime is None:
                logger.warning(f'Could not determine MIME type for extension {extension}. Defaulting to JPEG.')

            safe_mime = safe_mime if safe_mime is not None else MIME.J

            chapter.add_page(Image(uri=self.__create_chapter_page_uri(ch.get('chapter').get('hash'), page),
                                   name=f'{index}.{extension}',
                                   mime=safe_mime))
        return chapter

    def __fetch_chapter_hashes(self, chapter_id: str) -> tuple[str, list[str]]:
        """
        Fetches the chapter hashes and page file names for a given chapter ID. These details are necessary to construct
        the URLs for individual chapter pages.

        Args:
            chapter_id (str): The unique identifier of the chapter.

        Returns:
            tuple[str, list[str]]: A tuple containing the chapter hash and a list of page file names.
        """
        response = self.__make_request(url=urljoin(self.__HASH_URL, chapter_id))
        data: IHash = response.json()

        return (data.get('chapter').get('hash'), 
                data.get('chapter').get('data'))
    
    def __create_chapter_page_uri(self, hash: str, filename: str) -> str:
        """
        Constructs the URL for a chapter page given the chapter hash and the page file name.

        Args:
            hash (str): The hash of the chapter, used as part of the URL path.
            filename (str): The file name of the chapter page.

        Returns:
            str: The fully qualified URL to the chapter page.
        """
        return urljoin(self.__CHAPTER_PAGE_URL, f'{hash}/{filename}')

    def __create_chapter(self,
                         chapter: tuple[int, str],
                         with_symbolic_links: bool = False) -> Chapter:
        """
        Constructs a Chapter object for a given chapter tuple, optionally using symbolic links. If symbolic links are
        used, chapter pages are not pre-fetched but are instead represented as links.

        Args:
            chapter (tuple[int, str]): A tuple containing the chapter number and the chapter ID.
            with_symbolic_links (bool, optional): A flag indicating whether to use symbolic links for chapter pages. Defaults to False.

        Returns:
            Chapter: The constructed Chapter object.
        """        
        curr_chapter, chapter_id = chapter

        if with_symbolic_links:
            return Chapter(id=curr_chapter, 
                           link=SymbolicLink(link=urljoin(self.__HASH_URL, chapter_id)))
        else:
            ch = Chapter(id=curr_chapter)
            hash, files = self.__fetch_chapter_hashes(chapter_id)
        
            for index, page in enumerate(files):
                extension = page.split('.')[-1]
                safe_mime = mime.get_mime_safelly(extension.upper())
            
                if safe_mime is None:
                    logger.warning(f'Could not determine MIME type for extension {extension}. Defaulting to JPEG.')

                safe_mime = safe_mime if safe_mime is not None else MIME.J
                ch.add_page(Image(uri=self.__create_chapter_page_uri(hash, page),
                                  name=f'{index}.{extension}',
                                  mime=safe_mime))
        
            return ch
    
    def __list_chapters(self, manga_id: str) -> list[tuple[int, str]]:
        """
        Retrieves a list of chapters for a given manga ID. Each chapter is represented as a tuple containing the chapter
        number and the chapter ID.

        Args:
            manga_id (str): The unique identifier of the manga.

        Returns:
            list[tuple[int, str]]: A list of tuples, each representing a chapter of the manga.
        """
        response = self.__make_request(url=urljoin(self.__API_URL, f'manga/{manga_id}/aggregate'))
        
        data: IVolumesResponse = response.json()

        chapters = list()
        for volume in data.get('volumes', dict()):
            volume = data.get('volumes').get(volume)
            
            if volume is None: continue

            volume_chapters = volume.get('chapters', dict())
            
            for volume_key in volume_chapters:
                current_vol = volume_chapters.get(volume_key)

                if current_vol is None: continue

                chapters.append((current_vol.get('chapter'), current_vol.get('id')))
        
        return chapters
    
    def __extract_authors(self, relations: IRelations) -> list[Author]:
        """
        Extracts author information from a list of relationships within manga metadata, constructing Author objects
        for each author found.

        Args:
            relations (IRelations): A list of relationship objects from the manga metadata.

        Returns:
            list[Author]: A list of Author objects extracted from the relationships.
        """
        authors_data = [relationship for relationship in relations if relationship.get('type') == 'author']
        authors: list[Author] = []

        if len(authors_data) > 0:
            for author in authors_data:
                author = cast(AuthorRelation, author)
                authors.append(Author(name=author.get('attributes').get('name'),
                                      id=author.get('id')))
                
        return authors
    
    def __extract_genres(self, tags: list[IMangaTag]) -> list[Genre]:
        """
        Extracts genre information from a list of tags within manga metadata, constructing Genre objects for each tag
        that represents a genre.

        Args:
            tags (list[IMangaTag]): A list of tag objects from the manga metadata.

        Returns:
            list[Genre]: A list of Genre objects extracted from the tags.
        """
        return [Genre(id=tag.get('id'),
                      name=tag.get('attributes', {}).get('name', {}).get('en', 'unknown')) 
                    for tag in tags or []
                    if tag.get('type') == 'tag']
    
    def __get_cover(self, 
                    manga_id: str, 
                    relations: IRelations) -> Image:
        """
        Retrieves the cover image for a given manga ID from a list of relationships. If a cover image is found, an
        Image object is constructed and returned.

        Args:
            manga_id (str): The unique identifier of the manga.
            relations (IRelations): A list of relationship objects from the manga metadata.

        Returns:
            Image: An Image object representing the manga's cover image. Returns an Image object with an empty URI if no cover is found.
        """
        covers = [tag for tag in relations if tag.get('type') == 'cover_art']
        if len(covers) == 0: return Image(uri='')
        cover = cast(CoverArtRelation, covers[0])
        return Image(uri=self.__create_cover_uri(manga_id, cover.get("attributes").get("fileName")),
                     width=512)
    
    def __get_title(self, alt_titles: IAltTitles, title: str) -> Title:
        """
        Constructs a Title object for the manga, incorporating the English title, a Japanese title if available,
        and an alternative title.

        Args:
            alt_titles (IAltTitles): A list of alternative titles for the manga.
            title (str): The primary English title of the manga.

        Returns:
            Title: A Title object containing the English, Japanese, and an alternative title for the manga.
        """
        japanese_titles = [ title.get('ja-ro') for title in alt_titles if title.get('ja-ro') is not None ]
        japanese_title = japanese_titles[0] if len(japanese_titles) > 0 else None

        other_keys = list(alt_titles[-1].keys()) if len(alt_titles) > 0 else []
        other_key = other_keys[0] if len(other_keys) > 0 else ''

        return Title(english=title,
                     japanese=japanese_title or '',
                     other=alt_titles[-1].get(other_key, '') if len(alt_titles) > 0 else '')

    def __parse_full_manga(self, 
                           manga_data: IManga, 
                           with_symbolic_links: bool = False) -> Manga:
        """
        Parses the complete manga data retrieved from the Mangadex API, constructing a Manga object that includes
        details such as title, authors, genres, cover image, and chapters.

        Args:
            manga_data (IManga): The raw manga data from the Mangadex API.
            with_symbolic_links (bool, optional): Indicates whether to use symbolic links for chapters. Defaults to False.

        Returns:
            Manga: A fully constructed Manga object.
        """
        attrs = manga_data.get('attributes', dict())

        thumbnail = self.__get_cover(manga_data.get('id'), 
                                     manga_data.get('relationships'))
        
        status = 'completed' if attrs.get('status', "").lower() == 'completed' else 'ongoing'

        manga = Manga(title=self.__get_title(alt_titles=attrs.get('altTitles'),
                                             title=attrs.get('title', dict()).get('en') or ''),
                      id=manga_data.get('id'),
                      created_at=datetime.fromisoformat(attrs.get('createdAt')),
                      updated_at=datetime.fromisoformat(attrs.get('updatedAt')),
                      status=status,
                      url=urljoin(self.__SITE_URL, f'title/{manga_data.get("id")}'),
                      language=Language.get(attrs.get('originalLanguage').strip().lower().replace('-', '_'), 'unknown'),
                      authors=self.__extract_authors(manga_data.get('relationships', list())),
                      genres=self.__extract_genres(attrs.get('tags', list())),
                      thumbnail=thumbnail,
                      cover=thumbnail)
        
        chapter_list = self.__list_chapters(manga_id=str(manga.id))

        for chapter in chapter_list:
            manga.add_chapter(self.__create_chapter(chapter=chapter,
                                                    with_symbolic_links=with_symbolic_links))
            
        return manga
    
    def __parse_thumb(self, manga: IManga) -> Thumb:
        """
        Extracts minimal manga information to construct a Thumb object, primarily used for search results
        where detailed information is not necessary.

        Args:
            manga (IManga): The raw manga data from the Mangadex API.

        Returns:
            Thumb: A Thumb object containing the manga's ID, title, and cover image.
        """

        title = manga.get('attributes').get('title').get('en')
        return Thumb(id=manga.get('id'),
                     title=title,
                     url=urljoin(self.__SITE_URL, f'title/{manga.get("id")}'),
                     cover=self.__get_cover(manga_id=manga.get('id'),
                                            relations=manga.get('relationships', list())))
    
    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_GET_TTL_IN_SECONDS', 300)), 
           max_size=20).cache
    def get(self, 
            identifier: str,
            with_symbolic_links: bool = False) -> Manga:
        """
        Retrieves detailed information for a specific manga identified by its ID, constructing a Manga object.

        Args:
            identifier (str): The unique identifier of the manga to retrieve.
            with_symbolic_links (bool, optional): Indicates whether to construct the Manga object with symbolic links for chapters. Defaults to False.

        Returns:
            Manga: The Manga object containing detailed information about the specified manga.
        """
        response = self.__make_request(url=urljoin(self.__API_URL, f'manga/{identifier}'),
                                       params=[('includes[]', 'cover_art'),
                                               ('includes[]', 'author'),
                                               ('includes[]', 'artist')])

        result: IGetResult = response.json()
        manga_data = result.get('data')

        return self.__parse_full_manga(manga_data=manga_data,
                                       with_symbolic_links=with_symbolic_links)
        
    def __make_sort_query(self, sort: Sort) -> dict[str, str]:
        """
        Constructs a query parameter dictionary to define the sorting order for search results based on a Sort enumeration value.

        Args:
            sort (Sort): An enumeration value specifying the desired sort order for search results.

        Returns:
            dict[str, str]: A dictionary of query parameters to define the sorting order.
        """
        return { f'order[{sort.value if isinstance(sort, Sort) else sort}]': 'desc' }

    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_SEARCH_TTL_IN_SECONDS', 100)), 
           max_size=5).cache
    def search(self,
               query: str,
               page: int,
               sort: Sort = Sort.RECENT,
               per_page: int = 25) -> SearchResult:
        """
        Searches the Mangadex API for manga that match the given query string, optionally sorting the results
        and paginating them. Constructs and returns a SearchResult object containing the search results.
        
        Args:
            query (str): The search query string.
            page (int): The page number of the search results to retrieve.
            sort (Sort, optional): The sorting order of the search results. Defaults to Sort.RECENT.
            per_page (int, optional): The number of results per page. Defaults to 25.

        Returns:
            SearchResult: An object containing the paginated search results, including manga thumbnails.
        """
        logger.debug(f'Searching into Mangadex with args query={query};page={page};sort={sort}')

        params = [('title', query), *tuple(self.__make_sort_query(sort).items()),
                  ('includes[]', 'cover_art'), ('limit', per_page),
                  ('offset', per_page * (page - 1) if page > 1 else 0), ('contentRating[]', 'safe'),
                  ('contentRating[]', 'suggestive'), ('contentRating[]', 'erotica'),
                  ('order[createdAt]', 'desc'), ('hasAvailableChapters', 'true')]
        
        request_response = self.__make_request(url=urljoin(self.__API_URL, 'manga'),
                                               params=params)
        
        response: ISearchResult = request_response.json()

        total_results = response.get('total')
        total_pages = int(total_results / per_page)
        
        search_result = SearchResult(query=query,
                                     total_pages=total_pages,
                                     page=page,
                                     total_results=total_results)
        
        for result in response.get('data', []):
            search_result.results.append(self.__parse_thumb(manga=result))

        return search_result

    @Cache(max_age_seconds=int(os.getenv('ENMA_CACHING_PAGINATE_TTL_IN_SECONDS', 100)), 
           max_size=5).cache
    def paginate(self, page: int) -> Pagination:
        """
        Retrieves a specific page of manga listings from the Mangadex API, returning a Pagination object
        that includes a list of manga thumbnails for that page.

        Args:
            page (int): The page number of manga listings to retrieve.

        Returns:
            Pagination: An object containing the paginated list of manga thumbnails and pagination details.
        """
        logger.debug(f'Paginating with args page={page}')
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
                                total_results=response.get('total'))

        for result in response.get('data', []):            
            pagination.results.append(self.__parse_thumb(manga=result))

        return pagination

    def random(self, retry=0) -> Manga:
        """
        Fetches a random manga from the Mangadex API. If the first attempt fails, it will retry up to a specified number of times.

        Args:
            retry (int, optional): The number of retries to attempt in case of failure. Defaults to 0.

        Returns:
            Manga: A Manga object for the randomly selected manga.
        """
        response = self.__make_request(url=urljoin(self.__API_URL, f'manga/random'),
                                       params=[('includes[]', 'cover_art'),
                                               ('contentRating[]', 'safe'),
                                               ('contentRating[]', 'suggestive'),
                                               ('contentRating[]', 'erotica'),
                                               ('includes[]', 'author'),
                                               ('includes[]', 'artist')])

        result: IGetResult = response.json()

        manga = result.get('data')

        return self.__parse_full_manga(manga_data=manga,
                                       with_symbolic_links=True)
    
    def author_page(self,
                    author: str,
                    page: int) -> AuthorPage:
        """
        Fetches manga authored by a specific author. This method is not currently implemented for Mangadex
        and serves as a placeholder for potential future functionality.

        Args:
            author (str): The name or identifier of the author.
            page (int): The page number of results to retrieve.

        Raises:
            NotImplementedError: Indicates that this method is not supported or implemented.

        Returns:
            AuthorPage: An object containing a list of manga by the specified author. This is currently not implemented.
        """
        raise NotImplementedError('Mangadex does not support author page.')
