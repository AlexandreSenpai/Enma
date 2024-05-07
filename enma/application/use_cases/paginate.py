from dataclasses import dataclass

from pydantic import BaseModel, field_validator
from enma.application.core.handlers.error import InvalidRequest
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.application.core.utils.logger import logger
from enma.domain.entities.pagination import Pagination

class PaginateRequestDTO(BaseModel):
    page: int

    @field_validator("page")
    def validate_page(cls, page: int) -> int:
        if page <= 0:
            raise InvalidRequest(message='Page value must be greater than 0.')
        return int(page)
@dataclass
class PaginateResponseDTO:
    result: Pagination
    
class PaginateUseCase(IUseCase[PaginateRequestDTO, PaginateResponseDTO]):

    def __init__(self, manga_repository: IMangaRepository):
        self.__manga_repository = manga_repository

    def execute(self, dto: DTO[PaginateRequestDTO]) -> PaginateResponseDTO:
        logger.info(f'Retrieving page {dto.data.page}')
        result = self.__manga_repository.paginate(page=dto.data.page)
        
        return PaginateResponseDTO(result=result)
