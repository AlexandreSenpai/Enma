from NHentai.sync.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.sync.infra.adapters.repositories.hentai.interfaces.doujin import Doujin

class GetRandomDoujinUseCase:
    def __init__(self, nhentai_repo: NhentaiInterface):
        self.nhentai_repo = nhentai_repo
    
    def execute(self) -> Doujin:
        return self.nhentai_repo.get_random()