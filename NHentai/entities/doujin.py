from .base_entity import BaseClass
from .utils import Mimes
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin
from datetime import datetime

from ..base_wrapper import BaseWrapper

@dataclass
class Title(BaseClass):
    english: Optional[str]
    japanese: Optional[str]
    chinese: Optional[str]
    pretty: Optional[str]

    @classmethod
    def from_json(cls, json_object):
        args = {"english": json_object.get('english'),
                "japanese": json_object.get('japanese'),
                "chinese": json_object.get('chinese'),
                "pretty": json_object.get('pretty')}
        
        return cls(*args.values())

@dataclass
class DoujinPage(BaseClass):
    index: int
    media_id: int
    width: int
    height: int
    mime: str
    src: str

    @classmethod
    def from_json(cls, json_object: dict, page_index: int, media_id: str=None):
        args = {"index": page_index+1, 
                "media_id": media_id, 
                "width": json_object.get('w'), 
                "height": json_object.get('h'),
                "mime": Mimes[json_object.get('t').upper()].value, 
                "src": urljoin(BaseWrapper._IMAGE_BASE_URL, f'{media_id}/{page_index+1}.{Mimes[json_object.get("t").upper()].value}')}
        
        return cls(*args.values())

@dataclass
class Cover(BaseClass):
	media_id: int
	width: int
	height: int
	mime: str
	src: str

	@classmethod
	def from_json(cls, json_object: dict):
		args = {"media_id": json_object.get('media_id'),  
                        "width": json_object.get('w'), 
                        "height": json_object.get('h'),
                        "mime": Mimes[json_object.get('t').upper()].value, 
                        "src": urljoin(BaseWrapper._TINY_IMAGE_BASE_URL, f'{json_object.get("media_id")}/cover.{Mimes[json_object.get("t").upper()].value}')}
		
		return cls(*args.values())

@dataclass
class Thumbnail(BaseClass): ...

@dataclass
class Tag(BaseClass):
    id: int
    type: str
    name: str
    url: str
    count: int

    @classmethod
    def from_json(cls, json_object: dict):

        args = {"id": json_object.get('id'), 
                "type": json_object.get('type'), 
                "name": json_object.get('name'), 
                "url": urljoin(BaseWrapper._BASE_URL, json_object.get('url')), 
                "count": json_object.get('count')}

        return cls(*args.values())

@dataclass
class Doujin(BaseClass):
    id: int
    media_id: str
    upload_at: datetime
    url: str
    title: List[Title]
    tags: List[Tag]
    artists: List[Tag]
    languages: List[Tag]
    categories: List[Tag]
    characters: List[Tag]
    parodies: List[Tag]
    groups: List[Tag]
    cover: Cover
    images: List[DoujinPage]
    total_favorites: int = 0
    total_pages: int = 0

    @classmethod
    def from_json(cls, json_object: dict):

        ALL_TAGS = json_object.get('tags')
        MEDIA_ID = json_object.get('media_id')

        TAG_DICT = {'tag': [],
                    'artist': [],
                    'group': [],
                    'parody': [],
                    'character': [],
                    'category': [],
                    'language': []}

        for tag in ALL_TAGS:
                if TAG_DICT.get(tag.get('type')) is not None:
                    TAG_DICT[tag.get('type')].append(Tag.from_json(tag))

        COVER = Cover.from_json(json_object={**json_object.get('images').get('cover'), "media_id": MEDIA_ID})
        PAGES = [DoujinPage.from_json(page, index, MEDIA_ID)
                 for index, page in enumerate(json_object.get('images').get('pages'))]

        args = {"id": json_object.get('id'),
                "media_id": json_object.get('media_id'),
                "upload_at": datetime.fromtimestamp(json_object.get('upload_date')),
                "url": urljoin(BaseWrapper._BASE_URL, f'g/{json_object.get("id")}'),
                "title": Title.from_json(json_object.get('title', {})),
                "tags": [Tag.from_json(tag) for tag in ALL_TAGS],
                "artists": TAG_DICT['artist'],
                "languages": TAG_DICT['language'],
                "categories": TAG_DICT['category'],
                "characters": TAG_DICT['character'],
                "parodies": TAG_DICT['parody'],
                "groups": TAG_DICT['group'],
                "cover": COVER,
                "images": PAGES,
                "total_favorites": int(json_object.get('num_favorites')),
                "total_pages": len(PAGES)}
        
        return cls(*args.values())

@dataclass
class DoujinThumbnail(BaseClass):
	id: str
	media_id: str
	title: List[Title]
	languages: List[Tag]
	cover: Cover
	url: str
	tags: List[Tag]

	@classmethod
	def from_json(cls, json_object: dict):
                args = {"id": json_object.get('id'), 
                        "media_id": json_object.get('media_id'), 
                        "title": Title.from_json(json_object=json_object.get('title')),
                        "languages":  [Tag.from_json(tag) for tag in json_object.get('tags') if tag.get('type') == 'language'],
                        "cover": Cover.from_json(json_object={**json_object.get('images').get('cover'), "media_id": json_object.get('media_id')}),
                        "url": urljoin(BaseWrapper._BASE_URL, f'g/{json_object.get("id")}'),
                        "tags": [Tag.from_json(tag) for tag in json_object.get('tags')]}

                return cls(*args.values())
