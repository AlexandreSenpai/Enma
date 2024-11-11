"""
This module initializes the entrypoints library for the Enma application.
It sets up the necessary configurations and imports required for the entrypoints.
"""
from enum import Enum
from typing import Any, Generic, Optional, TypeVar, TypedDict, Union

from enma.application.core.handlers.error import InstanceError, InvalidResource, SourceNotAvailable, SourceWasNotDefined
from enma.application.core.interfaces.downloader_adapter import IDownloaderAdapter
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.saver_adapter import ISaverAdapter
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.application.use_cases.download_chapter import DownloadChapterRequestDTO, DownloadChapterResponseDTO, DownloadChapterUseCase, Threaded
from enma.application.use_cases.fetch_chapter_by_symbolic_link import FetchChapterBySymbolicLinkRequestDTO, FetchChapterBySymbolicLinkResponseDTO, FetchChapterBySymbolicLinkUseCase
from enma.application.use_cases.get_author_page import GetAuthorPageRequestDTO, GetAuthorPageResponseDTO, GetAuthorPageUseCase
from enma.application.use_cases.get_manga import GetMangaRequestDTO, GetMangaResponseDTO, GetMangaUseCase
from enma.application.use_cases.get_random import RandomResponseDTO, RandomUseCase
from enma.application.use_cases.paginate import PaginateRequestDTO, PaginateResponseDTO, PaginateUseCase
from enma.application.use_cases.search_manga import SearchMangaRequestDTO, SearchMangaResponseDTO, SearchMangaUseCase
from enma.domain.entities.author_page import AuthorPage
from enma.domain.entities.manga import Chapter, Manga
from enma.domain.entities.pagination import Pagination
from enma.domain.entities.search_result import SearchResult
from enma.infra.adapters.repositories.mangadex import Mangadex
from enma.infra.adapters.repositories.manganato import Manganato
from enma.infra.adapters.repositories.nhentai import NHentai, CloudFlareConfig
from enma.infra.core.interfaces.lib import IEnma
from enma.application.core.utils.logger import logger

class Sources(Enum):
    NHENTAI = 'nhentai'
    MANGADEX = 'mangadex'
    MANGANATO = 'manganato'

class ExtraConfigs(TypedDict):
    cloudflare_config: CloudFlareConfig

Source = TypeVar('Source', Sources, str)

class SourceManager(Generic[Source]):
    """
    Manages manga source repositories available to the Enma application, allowing for dynamic source selection at runtime.

    Attributes:
        source (Union[IMangaRepository, None]): The currently selected manga repository source.
        source_name (str): The name of the currently selected source.
    """

    def __init__(self) -> None:
        """
        Initializes the SourceManager with empty sources and no selected source.
        """
        self.__SOURCES: dict[str, IMangaRepository] = {}
        self.__CURRENT_SOURCE: Union[IMangaRepository, None] = None
        self.source_name = ''
    
    @property
    def source(self) -> Union[IMangaRepository, None]:
        return self.__CURRENT_SOURCE

    def get_source(self,
                   source_name: Union[Sources, Source]) -> IMangaRepository:
        """
        Retrieves a source repository by name.

        Args:
            source_name (Union[Sources, str]): The name of the source to retrieve, either as a string or an enum.

        Returns:
            IMangaRepository: The manga repository source.

        Raises:
            SourceNotAvailable: If the requested source is not available.
        """

        source_name = source_name.value if isinstance(source_name, Enum) else source_name
        source = self.__SOURCES.get(source_name)

        if source is None:
            raise SourceNotAvailable(f'{source_name} is not an available source.\nAvailable Sources {self.__SOURCES.keys()}')
        
        return source
    
    def set_source(self,
                   source_name: Union[Sources, Source]) -> None:
        """
        Sets the currently active source to the specified source name.

        Args:
            source_name (Union[Source, str]): The name of the source to activate, either as a string or an enum.
        """
        source = self.get_source(source_name=source_name)
        self.__CURRENT_SOURCE = source
        self.source_name = source_name

    def add_source(self,
                   source_name: Union[str, Sources, Source],
                   source: IMangaRepository) -> None:
        """
        Adds a new source repository to the available sources.

        Args:
            source_name (Union[str, Sources]): The name of the source to add.
            source (IMangaRepository): The manga repository source instance.

        Raises:
            InstanceError: If the provided source is not an instance of IMangaRepository.
        """
        if not isinstance(source, IMangaRepository):
            raise InstanceError('Provided source is not an instance of IMangaRepository.')
        
        self.__SOURCES[source_name if isinstance(source_name, str) else source_name.value] = source

    def remove_source(self,
                      source_name: Union[str, Source]) -> bool:

        name = source_name if isinstance(source_name, str) else source_name.value

        if name not in self.__SOURCES: 
            logger.warning(f"Source {name} not found.")
            return False
        
        del self.__SOURCES[name]
        return True
    
    def clear_sources(self) -> None:
        self.__SOURCES = dict()

def instantiate_source(callable):
    """
    Decorator function to ensure the current use case is instantiated with the current source.
    This is used to decorate methods of the Enma class that require a source to have been set.

    Args:
        callable: The method to be decorated.
    
    Returns:
        The wrapped method with source initialization logic.
    """
    def wrapper(self, *args, **kwargs):
        if self.source_manager.source is not None and \
            self._Enma__current_source_name != self.source_manager.source_name:
            self._Enma__initialize_use_case(source=self.source_manager.source)
            self._Enma__current_source_name = self.source_manager.source_name
        
        return callable(self, *args, **kwargs)
    return wrapper

class Enma(IEnma, Generic[Source]):
    """
    Main application class for Enma, providing interfaces to execute various manga-related use cases.
    Allows dynamic selection of manga sources and performs actions like fetching manga, searching, and downloading chapters.

    Attributes:
        source_manager (SourceManager[Source]): Manages the available sources and the current source selection.
    """
    def __init__(self, 
                 source: Optional[Source] = None, 
                 **kwargs) -> None:
        """
        Initializes the Enma application with optional default source selection and extra configurations.

        Args:
            source (Optional[Source], optional): The default source to be used. If provided, use cases will be initialized with this source.
        """
        self.__get_manga_use_case: Optional[IUseCase[GetMangaRequestDTO, GetMangaResponseDTO]] = None
        self.__search_manga_use_case: Optional[IUseCase[SearchMangaRequestDTO, SearchMangaResponseDTO]] = None
        self.__paginate_use_case: Optional[IUseCase[PaginateRequestDTO, PaginateResponseDTO]] = None
        self.__random_use_case: Optional[IUseCase[Any, RandomResponseDTO]] = None
        self.__downloader_use_case: Optional[IUseCase[DownloadChapterRequestDTO, DownloadChapterResponseDTO]] = None
        self.__get_author_page_use_case: Optional[IUseCase[GetAuthorPageRequestDTO, GetAuthorPageResponseDTO]] = None
        self.__fetch_chapter_by_symbolic_link_use_case: Optional[IUseCase[FetchChapterBySymbolicLinkRequestDTO, FetchChapterBySymbolicLinkResponseDTO]] = None
        self.__current_source_name: Optional[str] = None

        self.source_manager = SourceManager[Source](**kwargs)
        self.__create_default_sources()
        if source is not None: self.__initialize_use_case(source=self.source_manager.get_source(source_name=source))

    def __create_default_sources(self) -> None:
        """
        Creates and adds the default manga sources to the source manager. Currently, NHentai, Manganato, and Mangadex are added.
        """
        self.source_manager.add_source(Sources.NHENTAI, NHentai())
        self.source_manager.add_source(Sources.MANGANATO, Manganato())
        self.source_manager.add_source(Sources.MANGADEX, Mangadex())

    def __initialize_use_case(self, source: IMangaRepository) -> None:
        """
        Initializes the use cases with the given source repository. This method sets up all use cases available in Enma.

        Args:
            source (IMangaRepository): The source repository to initialize use cases with.
        """
        self.__get_manga_use_case = GetMangaUseCase(manga_repository=source)
        self.__search_manga_use_case = SearchMangaUseCase(manga_repository=source)     
        self.__paginate_use_case = PaginateUseCase(manga_repository=source)     
        self.__random_use_case = RandomUseCase(manga_repository=source)
        self.__downloader_use_case = DownloadChapterUseCase()  
        self.__get_author_page_use_case = GetAuthorPageUseCase(manga_repository=source)
        self.__fetch_chapter_by_symbolic_link_use_case = FetchChapterBySymbolicLinkUseCase(manga_repository=source)
    

    @instantiate_source
    def get(self, 
            identifier: str,
            with_symbolic_links: bool = True) -> Union[Manga, None]:
        """
        Retrieves detailed information for a specific manga identified by its ID.

        Args:
            identifier (str): The unique identifier of the manga to retrieve.
            with_symbolic_links (bool, optional): If True, fetches the manga with symbolic links to chapters. Defaults to True.

        Returns:
            Union[Manga, None]: The Manga object if found, None otherwise.

        Raises:
            SourceWasNotDefined: If no source has been defined prior to calling this method.
        """
        if self.__get_manga_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')

        response = self.__get_manga_use_case.execute(dto=DTO(data=GetMangaRequestDTO(identifier=identifier,
                                                                                     with_symbolic_links=with_symbolic_links)))
        
        if not response.found: return
        return response.manga
    
    @instantiate_source
    def search(self, 
               query: str, 
               page: int=1, 
               **kwargs) -> SearchResult:
        """
        Searches for manga that match the given query string.

        Args:
            query (str): The search query string.
            page (int, optional): The page number of the search results to retrieve. Defaults to 1.
            **kwargs: Additional parameters for search customization.

        Returns:
            SearchResult: An object containing the paginated search results, including manga thumbnails.

        Raises:
            SourceWasNotDefined: If no source has been defined prior to calling this method.
        """
        if self.__search_manga_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')
        
        response = self.__search_manga_use_case.execute(dto=DTO(data=SearchMangaRequestDTO(query=query,
                                                                                           page=page,
                                                                                           extra=kwargs)))
        
        return response.result
    
    @instantiate_source
    def paginate(self, 
                 page: int=1) -> Pagination:
        """
        Retrieves a specific page of manga listings.

        Args:
            page (int): The page number of manga listings to retrieve.

        Returns:
            Pagination: An object containing the paginated list of manga thumbnails and pagination details.

        Raises:
            SourceWasNotDefined: If no source has been defined prior to calling this method.
        """
        if self.__paginate_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')
        
        response = self.__paginate_use_case.execute(dto=DTO(data=PaginateRequestDTO(page=page)))

        return response.result
    
    @instantiate_source
    def random(self) -> Manga:
        """
        Fetches a random manga from the currently selected source.

        Returns:
            Manga: A Manga object for the randomly selected manga.

        Raises:
            SourceWasNotDefined: If no source has been defined prior to calling this method.
            NotImplementedError: If the current source does not support fetching an author's page.
        """
        if self.__random_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')
        
        response = self.__random_use_case.execute() 
        return response.result
    
    
    @instantiate_source
    def download_chapter(self, 
                         path: str, 
                         chapter: Chapter,
                         downloader: IDownloaderAdapter,
                         saver: ISaverAdapter,
                         threaded: Optional[Threaded] = None) -> None:
        """
        Downloads a manga chapter to the specified path using the provided downloader and saver adapters.

        Args:
            path (str): The filesystem path where the chapter should be saved.
            chapter (Chapter): The manga chapter to download.
            downloader (IDownloaderAdapter): The adapter to use for downloading the chapter pages.
            saver (ISaverAdapter): The adapter to use for saving the downloaded pages.
            threaded (Threaded): Determines whether the download should be performed in a threaded manner for concurrency.

        Raises:
            SourceWasNotDefined: If no source has been defined prior to calling this method.
        """
        if self.__downloader_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')
        
        self.__downloader_use_case.execute(dto=DTO(data=DownloadChapterRequestDTO(chapter=chapter,
                                                                                  path=path,
                                                                                  saver_adapter=saver,
                                                                                  downloader=downloader,
                                                                                  threaded=threaded)))
    
    @instantiate_source
    def author_page(self, 
                    author: str, 
                    page: int=1) -> AuthorPage:
        """
        Fetches manga authored by a specific author.

        Args:
            author (str): The name or identifier of the author.
            page (int): The page number of results to retrieve.

        Returns:
            AuthorPage: An object containing a list of manga by the specified author.

        Raises:
            SourceWasNotDefined: If no source has been defined prior to calling this method.
            NotImplementedError: If the current source does not support fetching an author's page.
        """
        if self.__get_author_page_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')
        
        return self.__get_author_page_use_case.execute(dto=DTO(data=GetAuthorPageRequestDTO(author=author,
                                                                                            page=page))).result

    @instantiate_source
    def fetch_chapter_by_symbolic_link(self, 
                                       chapter: Chapter) -> Chapter:
        """
        Fetches a manga chapter's details including pages and images by its symbolic link.

        Args:
            chapter (Chapter): The manga chapter to fetch, which must include a valid symbolic link.

        Returns:
            Chapter: An object containing the fetched chapter details such as pages and images.

        Raises:
            SourceWasNotDefined: If no source has been defined prior to calling this method.
            InvalidResource: If the provided chapter does not have a valid symbolic link.
        """
        if self.__fetch_chapter_by_symbolic_link_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')
        
        if chapter.link is None or chapter.link.link is None:
            raise InvalidResource('Chapter does not have a symbolic link.')
        
        response = self.__fetch_chapter_by_symbolic_link_use_case.execute(dto=DTO(data=FetchChapterBySymbolicLinkRequestDTO(link=chapter.link)))
        
        response.chapter.id = chapter.id

        return response.chapter
