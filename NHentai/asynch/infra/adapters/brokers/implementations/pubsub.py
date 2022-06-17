from concurrent.futures import Future
from dataclasses import asdict, dataclass
import json
import os
from typing import Optional, List
from attr import attributes

from google.cloud import pubsub_v1

from NHentai.asynch.infra.adapters.brokers.broker_interface import BrokerInterface

@dataclass
class Image:
    width: str
    height: str
    extension: str
    url: str
    index: Optional[str] = 0


@dataclass
class Images:
    pages: List[Image]
    cover: Image
    thumbnail: Image


@dataclass
class Source:
    id: int or str
    name: str
    url: str


@dataclass
class Title:
    pretty: str
    english: str
    japanese: str
    chinese: str

@dataclass
class Language:
    main: str
    english: str
    japanese: str
    chinese: str
    translated: str

@dataclass
class PubSubMessage:
    title: Title
    created_at: str
    updated_at: str
    language: Language
    source: Source
    tags: List[str]
    groups: List[str]
    characters: List[str]
    images: Images
    
    def to_json(self):
        return json.dumps(asdict(self))

    def to_dict(self):
        return asdict(self)


class PubSubBroker(BrokerInterface[PubSubMessage]):
    def __init__(self, topic: str, project_id: str):
        self.set_auth_environment_variable()
        self.client = pubsub_v1.PublisherClient()
        self.topic = self.client.topic_path(project=project_id, topic=topic)  
    
    def set_auth_environment_variable(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../core/auth/google/pubsub.json'))
    
    def publish(self, message: PubSubMessage):
        future: Future = self.client.publish(self.topic, 
                                             bytes(message.to_json(), encoding='utf-8'),
                                             action='create-doujin')
        return future.result()