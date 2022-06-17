from threading import Thread
from NHentai.sync.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.sync.infra.adapters.brokers.implementations.pubsub import PubSubMessage, Source, Image, Images, Title
from NHentai.sync.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface
from NHentai.sync.infra.adapters.repositories.hentai.interfaces import PopularPage
from NHentai.core.logging import logger

class GetPopularNowUseCase:
    def __init__(self, 
                 nhentai_repo: NhentaiInterface,
                 message_broker: BrokerInterface[PubSubMessage]):
        self.nhentai_repo = nhentai_repo
        self.message_broker = message_broker
        
    def send_to_pubsub(self, popular: PopularPage):
        try:
            for doujin in popular.doujins:
                Thread(target=self.message_broker.publish, 
                       args=(PubSubMessage(title=Title(pretty=doujin.title.pretty,
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
                                                                        url=doujin.cover.src))))).start()
        except Exception as e:
            logger.error(e)

    def execute(self) -> PopularPage:
        popular = self.nhentai_repo.get_popular_now()
        self.send_to_pubsub(popular)
        return popular