from dataclasses import dataclass

from pydantic import BaseModel
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.application.core.utils.logger import logger
from enma.domain.entities.manga import Chapter, SymbolicLink

class FetchChapterBySymbolicLinkRequestDTO(BaseModel):
    link: SymbolicLink

@dataclass
class FetchChapterBySymbolicLinkResponseDTO:
    chapter: Chapter
    
class FetchChapterBySymbolicLinkUseCase(IUseCase[FetchChapterBySymbolicLinkRequestDTO, FetchChapterBySymbolicLinkResponseDTO]):

    def __init__(self, manga_repository: IMangaRepository):
        self.__manga_repository = manga_repository

    def execute(self, dto: DTO[FetchChapterBySymbolicLinkRequestDTO]) -> FetchChapterBySymbolicLinkResponseDTO:
        logger.info(f'Fetching chapter by symbolic link: {dto.data.link}.')
        
        chapter = self.__manga_repository.fetch_chapter_by_symbolic_link(link=dto.data.link)
        
        return FetchChapterBySymbolicLinkResponseDTO(chapter=chapter)
