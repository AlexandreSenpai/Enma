import asyncio

from NHentai.asynch.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.asynch.infra.adapters.brokers.implementations.pubsub import Images, Language, PubSubMessage, Source, Title, Image
from NHentai.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.asynch.infra.adapters.repositories.hentai.interfaces.doujin import Doujin
from NHentai.core.logging import logger


class GetDoujinUseCase:
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
                language=Language(chinese=[chinese for chinese in doujin.languages if chinese.name.lower() == 'chinese'][0] or None,
                                english=[english for english in doujin.languages if english.name.lower() == 'english'][0] or None,
                                japanese=[japanese for japanese in doujin.languages if japanese.name.lower() == 'japanese'][0] or None,
                                translated=[translated for translated in doujin.languages if translated.name.lower() == 'translated'][0] or None),
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

    async def get_doujin(self, doujin_id: int):
        return await self.nhentai_repo.get_doujin(doujin_id=doujin_id)
    
    async def execute(self, doujin_id: int) -> Doujin:
        doujin = await self.get_doujin(doujin_id=doujin_id)
        self.loop.create_task(self.send_to_pubsub(doujin=doujin))
        return doujin