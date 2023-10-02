"""
This module initializes the entrypoints library for the Enma application.
It sets up the necessary configurations and imports required for the entrypoints.
"""
from enum import Enum
from typing import Any, Generic, Optional, TypeVar, TypedDict

from enma.application.core.handlers.error import InstanceError, SourceNotAvailable, SourceWasNotDefined
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.application.use_cases.get_manga import GetMangaRequestDTO, GetMangaResponseDTO, GetMangaUseCase
from enma.application.use_cases.get_random import RandomResponseDTO, RandomUseCase
from enma.application.use_cases.paginate import PaginateRequestDTO, PaginateResponseDTO, PaginateUseCase
from enma.application.use_cases.search_manga import SearchMangaRequestDTO, SearchMangaResponseDTO, SearchMangaUseCase
from enma.domain.entities.manga import Manga
from enma.domain.entities.pagination import Pagination
from enma.domain.entities.search_result import SearchResult
from enma.infra.adapters.repositories.manganato import Manganato
from enma.infra.adapters.repositories.nhentai import NHentai, CloudFlareConfig
from enma.infra.core.interfaces.lib import IEnma

class SourcesEnum(str, Enum):
    ...

class DefaultAvailableSources(SourcesEnum):
    NHENTAI = 'nhentai'
    MANGANATO = 'manganato'

class ExtraConfigs(TypedDict):
    cloudflare_config: CloudFlareConfig

AvailableSources = TypeVar('AvailableSources', bound=SourcesEnum)

class SourceManager(Generic[AvailableSources]):
    def __init__(self, **kwargs) -> None:
        self.__SOURCES: dict[str, IMangaRepository] = {'nhentai': NHentai(config=kwargs.get('cloudflare_config')),
                                                       'manganato': Manganato()}
        self.source = None
        self.source_name = ''
    
    def get_source(self,
                   source_name: AvailableSources | str) -> IMangaRepository:
        
        source_name = source_name.value if isinstance(source_name, Enum) else source_name
        source = self.__SOURCES.get(source_name)

        if source is None:
            raise SourceNotAvailable(f'{source_name} is not an available source.\nAvailable Sources {self.__SOURCES.keys()}')
        
        return source
    
    def set_source(self,
                   source_name: AvailableSources | str) -> None:
        source = self.get_source(source_name=source_name)
        self.source = source
        self.source_name = source_name

    def add_source(self,
                   source_name: str,
                   source: IMangaRepository) -> None:

        if not isinstance(source, IMangaRepository):
            raise InstanceError('Provided source is not an instance of IMangaRepository.')
        
        self.__SOURCES[source_name] = source

def instantiate_source(callable):
    def wrapper(self, *args, **kwargs):
        if self.source_manager.source is not None and \
            self._Enma__current_source_name != self.source_manager.source_name:
            self._Enma__initialize_use_case(source=self.source_manager.source)
            self._Enma__current_source_name = self.source_manager.source_name
        
        return callable(self, *args, **kwargs)
    return wrapper

class Enma(IEnma, Generic[AvailableSources]):
    def __init__(self, 
                 source: Optional[AvailableSources] = None, 
                 **kwargs) -> None:

        self.__get_manga_use_case: Optional[IUseCase[GetMangaRequestDTO, GetMangaResponseDTO]] = None
        self.__search_manga_use_case: Optional[IUseCase[SearchMangaRequestDTO, SearchMangaResponseDTO]] = None
        self.__paginate_use_case: Optional[IUseCase[PaginateRequestDTO, PaginateResponseDTO]] = None
        self.__random_use_case: Optional[IUseCase[Any, RandomResponseDTO]] = None
        self.__current_source_name = None

        self.source_manager = SourceManager[AvailableSources](**kwargs)
        if source is not None: self.__initialize_use_case(source=self.source_manager.get_source(source_name=source))

    def __initialize_use_case(self, source: IMangaRepository) -> None:
        self.__get_manga_use_case = GetMangaUseCase(manga_repository=source)
        self.__search_manga_use_case = SearchMangaUseCase(manga_repository=source)     
        self.__paginate_use_case = PaginateUseCase(manga_repository=source)     
        self.__random_use_case = RandomUseCase(manga_repository=source)     
        
    @instantiate_source
    def get(self, identifier: str) -> Manga | None:
        if self.__get_manga_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')

        response = self.__get_manga_use_case.execute(dto=DTO(data=GetMangaRequestDTO(identifier=identifier)))
        
        if not response.found: return
        return response.manga
    
    @instantiate_source
    def search(self, query: str, page: int, **kwargs) -> SearchResult:
        if self.__search_manga_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')
        
        response = self.__search_manga_use_case.execute(dto=DTO(data=SearchMangaRequestDTO(query=query,
                                                                                           extra=kwargs)))
        
        return response.result
    
    @instantiate_source
    def paginate(self, page: int) -> Pagination:
        if self.__paginate_use_case is None:
            raise SourceWasNotDefined('You must define a source before of performing actions.')
        
        response = self.__paginate_use_case.execute(dto=DTO(data=PaginateRequestDTO(page=page)))

        return response.result
    
    @instantiate_source
    def random(self) -> Manga:
        response = self.__random_use_case.execute() # type: ignore
        return response.result