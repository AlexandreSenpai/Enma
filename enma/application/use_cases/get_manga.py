from dataclasses import dataclass
from typing import Union

from pydantic import BaseModel, Field, validator
from enma.application.core.handlers.error import InvalidRequest
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.application.core.utils.logger import logger
from enma.domain.entities.manga import Manga

class GetMangaRequestDTO(BaseModel):
    identifier: str
    with_symbolic_links: bool = Field(default=False)

@dataclass
class GetMangaResponseDTO:
    found: bool
    manga: Union[Manga, None]
class GetMangaUseCase(IUseCase[GetMangaRequestDTO, GetMangaResponseDTO]):
    
    def __init__(self, manga_repository: IMangaRepository):
        self.__manga_repository = manga_repository

    def execute(self, dto: DTO[GetMangaRequestDTO]) -> GetMangaResponseDTO:
        logger.info(f'Fetching manga with identifier: {dto.data.identifier}.')

        manga = self.__manga_repository.get(identifier=dto.data.identifier,
                                            with_symbolic_links=dto.data.with_symbolic_links)
        
        if manga is None: return GetMangaResponseDTO(found=False, manga=None)
        
        return GetMangaResponseDTO(found=True, manga=manga)