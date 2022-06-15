from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.asynch.infra.adapters.repositories.hentai.interfaces.doujin import Doujin

class GetRandomDoujinUseCase:
    def __init__(self, nhentai_repo: NhentaiInterface):
        self.nhentai_repo = nhentai_repo
    
    async def execute(self) -> Doujin:
        return await self.nhentai_repo.get_random()