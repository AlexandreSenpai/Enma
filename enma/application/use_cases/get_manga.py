from dataclasses import dataclass
from typing import Union
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.domain.entities.manga import Manga

@dataclass
class GetMangaRequestDTO:
    identifier: str

@dataclass
class GetMangaResponseDTO:
    found: bool
    manga: Union[Manga, None]
    
class GetMangaUseCase(IUseCase[GetMangaRequestDTO, GetMangaResponseDTO]):

    def __init__(self, manga_repository: IMangaRepository):
        self.__manga_repository = manga_repository

    def execute(self, dto: DTO[GetMangaRequestDTO]) -> GetMangaResponseDTO:
        manga = self.__manga_repository.get(identifier=dto.data.identifier)
        
        if manga is None: return GetMangaResponseDTO(found=False, manga=None)
        
        return GetMangaResponseDTO(found=True, manga=manga)