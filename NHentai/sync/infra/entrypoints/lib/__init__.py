from NHentai.core.helpers.cloudflare import CloudFlareSettings
from NHentai.sync.application.use_cases.get_comments import GetCommentsUseCase
from NHentai.sync.application.use_cases.get_page import GetPageUseCase
from NHentai.core.interfaces.doujin import CommentPage
from NHentai.core.interfaces.page import Page
from NHentai.sync.infra.adapters.brokers.implementations.pubsub import PubSubBroker
from NHentai.sync.infra.adapters.repositories.hentai.implementations.nhentai import NHentaiAdapter
from NHentai.core.interfaces import Sort, Doujin, PopularPage 
from NHentai.sync.infra.adapters.request.http.implementations.sync import RequestsAdapter
from NHentai.sync.application.use_cases import (SearchDoujinUseCase,
                                                GetDoujinUseCase,
                                                GetRandomDoujinUseCase,
                                                GetPopularNowUseCase)
from NHentai.core.cache import Cache

class NHentai:
    
    def __init__(self, request_settings: CloudFlareSettings=None):
        self.request_settings = request_settings    
        self._NHENTAI_ADAPTER = NHentaiAdapter(request_adapter=RequestsAdapter(request_settings=self.request_settings))
        self._PUBSUB_MESSAGE_BROKER = PubSubBroker(topic='doujins', project_id='eroneko')
    
    @Cache(max_age_seconds=3600, max_size=1000, cache_key_position=1, cache_key_name='doujin_id').cache
    def get_doujin(self, doujin_id: int):
        return GetDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                message_broker=self._PUBSUB_MESSAGE_BROKER).execute(doujin_id=doujin_id)

    def get_random(self) -> Doujin:
        return GetRandomDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                      message_broker=self._PUBSUB_MESSAGE_BROKER).execute()
    
    def search(self, query: str, page: int = 1, sort: Sort = Sort.RECENT):
        return SearchDoujinUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                    message_broker=self._PUBSUB_MESSAGE_BROKER).execute(query=query, page=page, sort=sort)
    
    def get_popular_now(self) -> PopularPage:
        return GetPopularNowUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                                    message_broker=self._PUBSUB_MESSAGE_BROKER).execute()
        
    @Cache(max_age_seconds=3600, max_size=1000, cache_key_position=1, cache_key_name='doujin_id').cache
    def get_comments(self, doujin_id: int) -> CommentPage:
        return GetCommentsUseCase(nhentai_repo=self._NHENTAI_ADAPTER).execute(doujin_id=doujin_id)

    @Cache(max_age_seconds=3600, max_size=15, cache_key_position=1, cache_key_name='page').cache
    def get_page(self, page:int=1) -> Page:
        return GetPageUseCase(nhentai_repo=self._NHENTAI_ADAPTER,
                              message_broker=self._PUBSUB_MESSAGE_BROKER).execute(page=page)