import asyncio
from NHentai.asynch.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.asynch.infra.adapters.brokers.implementations.pubsub import PubSubMessage
from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.core.propagate import PropagateMessage

class SearchDoujinUseCase:
    def __init__(self, 
                 nhentai_repo: NhentaiInterface,
                 message_broker: BrokerInterface[PubSubMessage]):
        self.nhentai_repo = nhentai_repo
        self.message_broker = message_broker
        self.loop = asyncio.get_running_loop()
    
    async def execute(self, query: str, sort: str='recent', page: int=1, parallel_jobs: int=1):
        result = await self.nhentai_repo.search_doujin(search_term=query, sort=sort, page=page, parallel_jobs=parallel_jobs)
        self.loop.create_task(PropagateMessage.async_publish(adapter=self.message_broker, data=result.doujins))
        return result