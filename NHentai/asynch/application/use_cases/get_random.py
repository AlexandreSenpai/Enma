import asyncio
from NHentai.core.logging import logger
from NHentai.asynch.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.asynch.infra.adapters.brokers.implementations.pubsub import PubSubMessage, Title, Image, Images, Source
from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.asynch.infra.adapters.repositories.hentai.interfaces.doujin import Doujin

class GetRandomDoujinUseCase:
    def __init__(self, 
                 nhentai_repo: NhentaiInterface,
                 message_broker: BrokerInterface[PubSubMessage]):
        self.nhentai_repo = nhentai_repo
        self.message_broker = message_broker
        self.loop = asyncio.get_running_loop()
        
    async def send_to_pubsub(self, doujin: Doujin):
        try:
            self.message_broker.publish(message=PubSubMessage(
                title=Title(pretty=doujin.title.pretty,
                            chinese=doujin.title.chinese,
                            english=doujin.title.english,
                            japanese=doujin.title.japanese),
                language=[language.name for language in doujin.languages],
                created_at=doujin.upload_at,
                updated_at=doujin.upload_at,
                characters=[char.name for char in doujin.characters],
                groups=[group.name for group in doujin.groups],
                tags=[tag.name for tag in doujin.tags],
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
                                              url=doujin.cover.src))
            ))
        except Exception as e:
            logger.error(e)
    
    async def execute(self) -> Doujin:
        doujin = await self.nhentai_repo.get_random()
        self.loop.create_task(self.send_to_pubsub(doujin))
        return doujin