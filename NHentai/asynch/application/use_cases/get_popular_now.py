import asyncio

from NHentai.asynch.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.asynch.infra.adapters.brokers.implementations.pubsub import PubSubMessage
from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.core.interfaces import PopularPage
from NHentai.core.propagate import PropagateMessage

class GetPopularNowUseCase:
    def __init__(self, 
                 nhentai_repo: NhentaiInterface,
                 message_broker: BrokerInterface[PubSubMessage]):
        self.nhentai_repo = nhentai_repo
        self.message_broker = message_broker
        self.loop = asyncio.get_running_loop()

    async def execute(self) -> PopularPage:
        popular = await self.nhentai_repo.get_popular_now()
        self.loop.create_task(PropagateMessage.async_publish(adapter=self.message_broker, data=popular.doujins))
        return popular