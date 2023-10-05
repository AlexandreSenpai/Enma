from dataclasses import dataclass, field
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.interfaces.use_case import DTO, IUseCase
from enma.domain.entities.search_result import SearchResult

@dataclass
class SearchMangaRequestDTO:
    query: str
    page: int = field(default=1)
    extra: dict[str, str | int] = field(default_factory=dict)

@dataclass
class SearchMangaResponseDTO:
    result: SearchResult
    
class SearchMangaUseCase(IUseCase[SearchMangaRequestDTO, SearchMangaResponseDTO]):

    def __init__(self, manga_repository: IMangaRepository):
        self.__manga_repository = manga_repository

    def execute(self, dto: DTO[SearchMangaRequestDTO]) -> SearchMangaResponseDTO:
        result = self.__manga_repository.search(query=dto.data.query,
                                                page=dto.data.page,
                                                **dto.data.extra)
        
        return SearchMangaResponseDTO(result=result)