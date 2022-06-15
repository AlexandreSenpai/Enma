from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.asynch.infra.adapters.repositories.hentai.interfaces.doujin import Doujin


class GetDoujinUseCase:
    def __init__(self, nhentai_repo: NhentaiInterface):
        self.nhentai_repo = nhentai_repo

    async def get_doujin(self, doujin_id: int):
        return await self.nhentai_repo.get_doujin(doujin_id=doujin_id)
    
    async def execute(self, doujin_id: int) -> Doujin:
        return await self.get_doujin(doujin_id=doujin_id)