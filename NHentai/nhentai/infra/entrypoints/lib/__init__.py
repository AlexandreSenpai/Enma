from NHentai.nhentai.infra.adapters.repositories.hentai.implementations.nhentai import NHentaiAdapter
from NHentai.nhentai.infra.adapters.repositories.hentai.interfaces import Sort, Doujin
from NHentai.nhentai.infra.adapters.request.implementations.http import RequestsAdapter
from NHentai.nhentai.application.use_cases import (SearchDoujinUseCase,
                                                   GetDoujinUseCase,
                                                   GetRandomDoujinUseCase,
                                                   GetPopularNowUseCase)

class NHentai:
    _NHENTAI_ADAPTER = NHentaiAdapter(request_adapter=RequestsAdapter())
    
    def get_doujin(self, doujin_id: int):
        return GetDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER).execute(doujin_id=doujin_id)

    def get_random(self) -> Doujin:
        return GetRandomDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER).execute()
    
    def search(self, query: str, page: int = 1, sort: Sort = Sort.RECENT):
        return SearchDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER).execute(query=query, page=page, sort=sort)
    
    def get_popular_now(self):
        return GetPopularNowUseCase(nhentai_repo=self._NHENTAI_ADAPTER).execute()