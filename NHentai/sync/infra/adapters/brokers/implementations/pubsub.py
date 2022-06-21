from concurrent.futures import Future
from dataclasses import asdict, dataclass
import json
from NHentai.core.auth.google import information 
from typing import Optional, List

from google.cloud import pubsub_v1
from google.oauth2 import service_account

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
class PubSubMessage:
    message_id: str
    title: Title
    created_at: str
    updated_at: str
    languages: List[str]
    parodies: List[str]
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
        self.client = self.create_client()
        self.topic = self.client.topic_path(project=project_id, topic=topic)  
    
    def create_client(self) -> pubsub_v1.PublisherClient:
        creds = service_account.Credentials.from_service_account_info(info=information)
        return pubsub_v1.PublisherClient(credentials=creds)
    
    def publish(self, message: PubSubMessage):
        future: Future = self.client.publish(self.topic, 
                                             bytes(message.to_json(), encoding='utf-8'),
                                             action='create-doujin')
        return future.result()