from NHentai.sync.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.sync.infra.adapters.repositories.hentai.interfaces import PopularPage

class GetPopularNowUseCase:
    def __init__(self, nhentai_repo: NhentaiInterface):
        self.nhentai_repo = nhentai_repo
    
    def execute(self) -> PopularPage:
        return self.nhentai_repo.get_popular_now()