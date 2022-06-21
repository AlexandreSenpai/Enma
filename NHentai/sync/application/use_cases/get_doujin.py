from NHentai.core.propagate import PropagateMessage
from NHentai.sync.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.sync.infra.adapters.brokers.implementations.pubsub import PubSubMessage
from NHentai.sync.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.core.interfaces import Doujin

class GetDoujinUseCase:
    def __init__(self, 
                 nhentai_repo: NhentaiInterface,
                 message_broker: BrokerInterface[PubSubMessage]):
        self.nhentai_repo = nhentai_repo
        self.message_broker = message_broker

    def get_doujin(self, doujin_id: int):
        return self.nhentai_repo.get_doujin(doujin_id=doujin_id)
    
    def execute(self, doujin_id: int) -> Doujin:
        doujin = self.get_doujin(doujin_id=doujin_id)
        PropagateMessage.publish(adapter=self.message_broker, data=[doujin])
        return doujin