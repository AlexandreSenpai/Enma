import asyncio

from NHentai.asynch.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.asynch.infra.adapters.brokers.implementations.pubsub import PubSubMessage
from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.core.interfaces.doujin import Doujin
from NHentai.core.propagate import PropagateMessage


class GetDoujinUseCase:
    def __init__(self, 
                 nhentai_repo: NhentaiInterface,
                 message_broker: BrokerInterface[PubSubMessage]):
        self.nhentai_repo = nhentai_repo
        self.message_broker = message_broker
        self.loop = asyncio.get_running_loop()

    async def get_doujin(self, doujin_id: int):
        return await self.nhentai_repo.get_doujin(doujin_id=doujin_id)
    
    async def execute(self, doujin_id: int) -> Doujin:
        doujin = await self.get_doujin(doujin_id=doujin_id)
        self.loop.create_task(PropagateMessage.async_publish(adapter=self.message_broker, data=[doujin]))
        return doujin