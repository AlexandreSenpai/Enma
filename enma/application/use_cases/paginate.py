from dataclasses import dataclass
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.domain.entities.pagination import Pagination

@dataclass
class PaginateRequestDTO:
    page: int

@dataclass
class PaginateResponseDTO:
    result: Pagination
    
class PaginateUseCase(IUseCase[PaginateRequestDTO, PaginateResponseDTO]):

    def __init__(self, manga_repository: IMangaRepository):
        self.__manga_repository = manga_repository

    def execute(self, dto: DTO[PaginateRequestDTO]) -> PaginateResponseDTO:
        result = self.__manga_repository.paginate(page=dto.data.page)
        
        return PaginateResponseDTO(result=result)