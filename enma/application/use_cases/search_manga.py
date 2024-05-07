from dataclasses import dataclass
from typing import Union

from pydantic import BaseModel, Field, field_validator
from enma.application.core.handlers.error import InvalidRequest
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.application.core.utils.logger import logger
from enma.domain.entities.search_result import SearchResult

class SearchMangaRequestDTO(BaseModel):
    query: str
    page: int = Field(default=1)
    extra: dict[str, Union[str, int]] = Field(default_factory=dict)

    @field_validator("page")
    def validate_page(cls, page: int) -> int:
        if page <= 0:
            raise InvalidRequest(message='Page value must be greater than 0.')
        return int(page)

@dataclass
class SearchMangaResponseDTO:
    result: SearchResult
    
class SearchMangaUseCase(IUseCase[SearchMangaRequestDTO, SearchMangaResponseDTO]):

    def __init__(self, manga_repository: IMangaRepository):
        self.__manga_repository = manga_repository

    def execute(self, dto: DTO[SearchMangaRequestDTO]) -> SearchMangaResponseDTO:
        logger.info(f'Searching for {dto.data.query}.')
        result = self.__manga_repository.search(query=dto.data.query,
                                                page=dto.data.page,
                                                **dto.data.extra)
        
        return SearchMangaResponseDTO(result=result)
