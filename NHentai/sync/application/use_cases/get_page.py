from NHentai.core.propagate import PropagateMessage
from NHentai.sync.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.sync.infra.adapters.brokers.implementations.pubsub import PubSubMessage
from NHentai.sync.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface

class GetPageUseCase:
    def __init__(self, 
                 nhentai_repo: NhentaiInterface,
                 message_broker: BrokerInterface[PubSubMessage]):
        self.nhentai_repo = nhentai_repo
        self.message_broker = message_broker
    
    def execute(self, page: int=1):
        result = self.nhentai_repo.get_page(page=page)
        PropagateMessage.publish(adapter=self.message_broker, data=result.doujins)
        return result