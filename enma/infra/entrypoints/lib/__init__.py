from enum import Enum
from typing import TypedDict
from enma.application.core.handlers.error import SourceNotAvailable
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO
from enma.application.use_cases.get_manga import GetMangaRequestDTO, GetMangaUseCase
from enma.domain.entities.Manga import Manga
from enma.infra.adapters.repositories.nhentai import NHentai, CloudFlareConfig
from enma.infra.core.interfaces.lib import IEnma

class AvailableSources(Enum):
    NHENTAI = 'nhentai'

class ExtraConfigs(TypedDict):
    cloudflare_config: CloudFlareConfig

class Enma(IEnma):
    def __init__(self, 
                 source: AvailableSources, 
                 **kwargs) -> None:
        self.__source = self.__get_source(source_name=source, **kwargs)
        self.__get_manga_use_case = GetMangaUseCase(manga_repository=self.__source)

    def __get_source(self,
                     source_name: AvailableSources,
                     **kwargs) -> IMangaRepository:
        SOURCES = {'nhentai': NHentai(config=kwargs.get('cloudflare_config'))}
        
        source = SOURCES.get(source_name.value)

        if source is None:
            raise SourceNotAvailable(f'{source_name.value} is not an available source.')
        
        return source
    
    def get(self, identifier: str) -> Manga | None:
        response = self.__get_manga_use_case.execute(dto=DTO(data=GetMangaRequestDTO(identifier=identifier)))
        
        if not response.found: return
        return response.manga