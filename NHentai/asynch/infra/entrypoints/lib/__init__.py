from NHentai.asynch.infra.adapters.brokers.implementations.pubsub import PubSubBroker
from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NHentaiAdapter
from NHentai.asynch.infra.adapters.repositories.hentai.interfaces import Sort, Doujin, PopularPage 
from NHentai.asynch.infra.adapters.request.http.implementations.asynk import RequestsAdapter
from NHentai.asynch.application.use_cases import (SearchDoujinUseCase,
                                                   GetDoujinUseCase,
                                                   GetRandomDoujinUseCase,
                                                   GetPopularNowUseCase)

class NHentaiAsync:
    _NHENTAI_ADAPTER = NHentaiAdapter(request_adapter=RequestsAdapter())
    _PUBSUB_MESSAGE_BROKER = PubSubBroker(topic='doujins', project_id='eroneko')
    
    async def get_doujin(self, doujin_id: int):
        return await GetDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                      message_broker=self._PUBSUB_MESSAGE_BROKER).execute(doujin_id=doujin_id)

    async def get_random(self) -> Doujin:
        return await GetRandomDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                            message_broker=self._PUBSUB_MESSAGE_BROKER).execute()
    
    async def search(self, query: str, page: int = 1, sort: Sort = Sort.RECENT):
        return await SearchDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                         message_broker=self._PUBSUB_MESSAGE_BROKER).execute(query=query, page=page, sort=sort)
    
    async def get_popular_now(self) -> PopularPage:
        return await GetPopularNowUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                          message_broker=self._PUBSUB_MESSAGE_BROKER).execute()