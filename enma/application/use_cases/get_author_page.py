from dataclasses import dataclass, field
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.application.core.utils.logger import logger
from enma.domain.entities.author_page import AuthorPage
from pydantic import BaseModel, Field

class GetAuthorPageRequestDTO(BaseModel):
    author: str
    page: int = Field(default=1)

@dataclass
class GetAuthorPageResponseDTO:
    result: AuthorPage
    
class GetAuthorPageUseCase(IUseCase[GetAuthorPageRequestDTO, GetAuthorPageResponseDTO]):

    def __init__(self, manga_repository: IMangaRepository):
        self.__manga_repository = manga_repository

    def execute(self, dto: DTO[GetAuthorPageRequestDTO]) -> GetAuthorPageResponseDTO:
        logger.info(f'Retrieving {dto.data.author} page.')
        result = self.__manga_repository.author_page(author=dto.data.author,
                                                     page=dto.data.page)
        
        return GetAuthorPageResponseDTO(result=result)
