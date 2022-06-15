from NHentai.sync.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.sync.infra.adapters.repositories.hentai.interfaces.doujin import Doujin


class GetDoujinUseCase:
    def __init__(self, nhentai_repo: NhentaiInterface):
        self.nhentai_repo = nhentai_repo

    def get_doujin(self, doujin_id: int):
        return self.nhentai_repo.get_doujin(doujin_id=doujin_id)
    
    def execute(self, doujin_id: int) -> Doujin:
        doujin = self.get_doujin(doujin_id=doujin_id)
        return doujin