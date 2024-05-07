from dataclasses import dataclass
from typing import Any
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import IUseCase
from enma.application.core.utils.logger import logger
from enma.domain.entities.manga import Manga

@dataclass
class RandomResponseDTO:
    result: Manga
    
class RandomUseCase(IUseCase[Any, RandomResponseDTO]):

    def __init__(self, manga_repository: IMangaRepository):
        self.__manga_repository = manga_repository

    def execute(self) -> RandomResponseDTO:
        logger.info(f'Fetching random manga.')
        result = self.__manga_repository.random()
        
        return RandomResponseDTO(result=result)
