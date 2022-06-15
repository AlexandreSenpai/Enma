from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.asynch.infra.adapters.repositories.hentai.interfaces import PopularPage

class GetPopularNowUseCase:
    def __init__(self, nhentai_repo: NhentaiInterface):
        self.nhentai_repo = nhentai_repo
    
    async def execute(self) -> PopularPage:
        return await self.nhentai_repo.get_popular_now()