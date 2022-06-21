from uuid import uuid4

from NHentai.asynch.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.asynch.infra.adapters.brokers.implementations.pubsub import Images, PubSubMessage, Title, Source, Image
from NHentai.core.interfaces.doujin import Doujin
from NHentai.core.logging import logger

class PropagateMessage:
    @staticmethod
    def create_payload(doujin: Doujin) -> PubSubMessage:
        if not isinstance(doujin, Doujin): return {}
        return PubSubMessage(
                    message_id=str(uuid4()),
                    title=Title(pretty=doujin.title.pretty,
                                chinese=doujin.title.chinese,
                                english=doujin.title.english,
                                japanese=doujin.title.japanese),
                    languages=[language.name for language in doujin.languages],
                    created_at=doujin.upload_at,
                    updated_at=doujin.upload_at,
                    characters=[char.name for char in doujin.characters],
                    groups=[group.name for group in doujin.groups],
                    tags=[tag.name for tag in doujin.tags],
                    parodies=[parodies.name for parodies in doujin.parodies],
                    source=Source(id=doujin.id,
                                name='nhentai',
                                url=f'https://nhentai.net/g/{doujin.id}/'),
                    images=Images(pages=[Image(width=page.width,
                                            height=page.height,
                                            extension=page.mime,
                                            index=index,
                                            url=page.src) for index, page in enumerate(doujin.images)],
                                cover=Image(width=doujin.cover.width,
                                            height=doujin.cover.height,
                                            extension=doujin.cover.mime,
                                            url=doujin.cover.src),
                                thumbnail=Image(width=doujin.cover.width,
                                                height=doujin.cover.height,
                                                extension=doujin.cover.mime,
                                                url=doujin.cover.src)))
    
    @staticmethod
    def publish(adapter: BrokerInterface, data):
        try:
            if not isinstance(data, list):
                data = [data]
            
            for doujin in data:
                adapter.publish(message=PropagateMessage.create_payload(doujin))
        except Exception as e:
            logger.debug(e)
            
    @staticmethod
    async def async_publish(adapter: BrokerInterface, data):
        try:
            if not isinstance(data, list):
                data = [data]

            for doujin in data:
                adapter.publish(message=PropagateMessage.create_payload(doujin))
        except Exception as e:
            logger.debug(e)