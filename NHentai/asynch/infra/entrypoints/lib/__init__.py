from NHentai.asynch.application.use_cases.get_comments import GetCommentsUseCase
from NHentai.asynch.application.use_cases.get_page import GetPageUseCase
from NHentai.asynch.infra.adapters.brokers.implementations.pubsub import PubSubBroker
from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NHentaiAdapter
from NHentai.core.helpers.cloudflare import CloudFlareSettings
from NHentai.core.interfaces import Sort, Doujin, PopularPage, CommentPage, Page
from NHentai.asynch.infra.adapters.request.http.implementations.asynk import RequestsAdapter
from NHentai.asynch.application.use_cases import (SearchDoujinUseCase,
                                                   GetDoujinUseCase,
                                                   GetRandomDoujinUseCase,
                                                   GetPopularNowUseCase)
from NHentai.core.cache import Cache

class NHentaiAsync:
    
    def __init__(self, request_settings: CloudFlareSettings=None):
        self.request_settings = request_settings    
        self._NHENTAI_ADAPTER = NHentaiAdapter(request_adapter=RequestsAdapter(request_settings=self.request_settings))
        self._PUBSUB_MESSAGE_BROKER = PubSubBroker(topic='doujins', project_id='eroneko')
    
    @Cache(max_age_seconds=3600, max_size=1000, cache_key_position=1, cache_key_name='doujin_id').async_cache
    async def get_doujin(self, doujin_id: int):
        return await GetDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                      message_broker=self._PUBSUB_MESSAGE_BROKER).execute(doujin_id=doujin_id)

    async def get_random(self) -> Doujin:
        return await GetRandomDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                            message_broker=self._PUBSUB_MESSAGE_BROKER).execute()
    
    async def search(self, query: str, page: int = 1, sort: Sort = Sort.RECENT, parallel_jobs:int=1):
        return await SearchDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                         message_broker=self._PUBSUB_MESSAGE_BROKER).execute(query=query, page=page, sort=sort, parallel_jobs=parallel_jobs)
    
    async def get_popular_now(self) -> PopularPage:
        return await GetPopularNowUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                          message_broker=self._PUBSUB_MESSAGE_BROKER).execute()
    
    @Cache(max_age_seconds=3600, max_size=1000, cache_key_position=1, cache_key_name='doujin_id').async_cache
    async def get_comments(self, doujin_id: int) -> CommentPage:
        return await GetCommentsUseCase(nhentai_repo=self._NHENTAI_ADAPTER).execute(doujin_id=doujin_id)

    @Cache(max_age_seconds=3600, max_size=15, cache_key_position=1, cache_key_name='page').async_cache
    async def get_page(self, page:int=1) -> Page:
        return await GetPageUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                    message_broker=self._PUBSUB_MESSAGE_BROKER).execute(page=page)