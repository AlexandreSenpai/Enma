from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface

class SearchDoujinUseCase:
    def __init__(self, nhentai_repo: NhentaiInterface):
        self.nhentai_repo = nhentai_repo
    
    async def execute(self, query: str, sort: str='recent', page: int=1):
        return await self.nhentai_repo.search_doujin(search_term=query, sort=sort, page=page)