from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin
from ..base_wrapper import BaseWrapper

@dataclass
class Title:
    english: Optional[str]
    japanese: Optional[str]
    chinese: Optional[str]
    pretty: Optional[str]

    @classmethod
    def from_json(cls, json_object):
        args = {"english": json_object.get('title', {}).get('english'),
                "japanese": json_object.get('title', {}).get('japanese'),
                "chinese": json_object.get('title', {}).get('chinese'),
                "pretty": json_object.get('title', {}).get('pretty')}
        
        return cls(*args.values())

@dataclass
class Page:
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
                "mime": BaseWrapper._MIMES[json_object.get('t')], 
                "src": urljoin(BaseWrapper._IMAGE_BASE_URL, f'{media_id}/{page_index+1}.{BaseWrapper._MIMES[json_object.get("t")]}')}
        
        return cls(*args.values())

@dataclass
class Cover(Page): ...

@dataclass
class Thumbnail(Page): ...

@dataclass
class Tag:
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
class Doujin:
    id: str
    title: List[Title]
    tags: List[Tag]
    artists: List[Tag]
    languages: List[Tag]
    categories: List[Tag]
    characters: List[Tag]
    parodies: List[Tag]
    groups: List[Tag]
    images: List[Page]
    total_pages: int = 0

@dataclass
class DoujinThumbnail:
    id: str
    media_id: str
    title: str
    lang: str
    cover: str
    url: str
    tags: list

    @classmethod
    def from_json(cls, json_object: dict):
        args = {"id": json_object.get('id'), 
                "media_id": json_object.get('media_id'), 
                "title": Title(english=json_object.get('title', {}).get('english'), 
                               japanese=json_object.get('title', {}).get('japanese'), 
                               chinese=json_object.get('title', {}).get('chinese'),
                               pretty=json_object.get('title', {}).get('pretty')),
                "lang": BaseWrapper._get_lang_by_title(title=json_object.get('title', {}).get('english')),
                "cover": Cover(index=1,
                               media_id=json_object.get('media_id'),
                               mime=BaseWrapper._MIMES[json_object.get("images").get("cover").get("t")],
                               width=json_object.get("images").get("cover").get("w"),
                               height=json_object.get("images").get("cover").get("h"),
                               src=urljoin(BaseWrapper._TINY_IMAGE_BASE_URL, f'{json_object.get("media_id")}/cover.{BaseWrapper._MIMES[json_object.get("images").get("cover").get("t")]}')),
                "url": urljoin(BaseWrapper._BASE_URL, f'g/{json_object.get("id")}'),
                "tags": [Tag.from_json(tag) for tag in json_object.get('tags')]}

        return cls(*args.values())
