from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

from .utils import Mimes

from .base_dataclass import BaseDataclass

@dataclass
class Title(BaseDataclass):
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
class DoujinPage(BaseDataclass):
    index: int
    media_id: int
    width: int
    height: int
    mime: str
    src: str

    @classmethod
    def from_json(cls, json_object: dict, image_base_url_prefix: str, page_index: int, media_id: str=None):
        args = {"index": page_index+1, 
                "media_id": media_id, 
                "width": json_object.get('w'), 
                "height": json_object.get('h'),
                "mime": Mimes[json_object.get('t').upper()].value, 
                "src": urljoin(image_base_url_prefix, f'{media_id}/{page_index+1}.{Mimes[json_object.get("t").upper()].value}')}
        
        return cls(*args.values())

@dataclass
class Cover(BaseDataclass):
	media_id: int
	width: int
	height: int
	mime: str
	src: str

	@classmethod
	def from_json(cls, json_object: dict, tiny_image_base_url_prefix: str):
		args = {"media_id": json_object.get('media_id'),  
                        "width": json_object.get('w'), 
                        "height": json_object.get('h'),
                        "mime": Mimes[json_object.get('t').upper()].value, 
                        "src": urljoin(tiny_image_base_url_prefix, f'{json_object.get("media_id")}/cover.{Mimes[json_object.get("t").upper()].value}')}
		
		return cls(*args.values())

@dataclass
class Thumbnail(BaseDataclass): ...

@dataclass
class Tag(BaseDataclass):
    id: int
    type: str
    name: str
    url: str
    count: int

    @classmethod
    def from_json(cls, json_object: dict, base_url: str):

        args = {"id": json_object.get('id'), 
                "type": json_object.get('type'), 
                "name": json_object.get('name'), 
                "url": urljoin(base_url, json_object.get('url')), 
                "count": json_object.get('count')}

        return cls(*args.values())

@dataclass
class Doujin(BaseDataclass):
    id: int
    media_id: str
    upload_at: str
    url: str
    title: Title
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
    def from_json(cls, 
                  json_object: dict, 
                  base_url: str, 
                  image_base_url_prefix: str, 
                  tiny_image_base_url_prefix: str):

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
                    TAG_DICT[tag.get('type')].append(Tag.from_json(tag, base_url=base_url))

        COVER = Cover.from_json(json_object={**json_object.get('images').get('cover'), "media_id": MEDIA_ID}, tiny_image_base_url_prefix=tiny_image_base_url_prefix)
        PAGES = [DoujinPage.from_json(json_object=page, image_base_url_prefix=image_base_url_prefix, page_index=index, media_id=MEDIA_ID)
                 for index, page in enumerate(json_object.get('images').get('pages'))]

        args = {"id": int(json_object.get('id')),
                "media_id": int(json_object.get('media_id')),
                "upload_at": datetime.fromtimestamp(json_object.get('upload_date')).strftime('%Y-%m-%d %H:%M:%S'),
                "url": urljoin(base_url, f'g/{json_object.get("id")}'),
                "title": Title.from_json(json_object.get('title', {})),
                "tags": [Tag.from_json(tag, base_url=base_url) for tag in ALL_TAGS],
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
class DoujinThumbnail(BaseDataclass):
	id: str
	media_id: str
	title: List[Title]
	languages: List[Tag]
	cover: Cover
	url: str
	tags: List[Tag]

	@classmethod
	def from_json(cls, json_object: dict, base_url: str):
                args = {"id": json_object.get('id'), 
                        "media_id": json_object.get('media_id'), 
                        "title": Title.from_json(json_object=json_object.get('title')),
                        "languages": [Tag.from_json(tag) for tag in json_object.get('tags') if tag.get('type') == 'language'],
                        "cover": Cover.from_json(json_object={**json_object.get('images').get('cover'), "media_id": json_object.get('media_id')}),
                        "url": urljoin(base_url, f'g/{json_object.get("id")}'),
                        "tags": [Tag.from_json(tag) for tag in json_object.get('tags')]}

                return cls(*args.values())

@dataclass
class User(BaseDataclass):
        id: int
        username: str
        slug: str
        avatar_url: str
        is_superuser: bool
        is_staff: bool

@dataclass
class Comment(BaseDataclass):
        id: int
        gallery_id: int
        poster: User
        post_date: int
        body: str
        
        @classmethod
        def from_json(cls, 
                        json_object: dict, 
                        avatar_url: str):

                user = User(id=json_object.get('poster', {}).get('id'),
                            username=json_object.get('poster', {}).get('username'),
                            avatar_url=urljoin(avatar_url, json_object.get('poster', {}).get('avatar_url')),
                            is_staff=json_object.get('poster', {}).get('is_staff'),
                            is_superuser=json_object.get('poster', {}).get('is_superuser'),
                            slug=json_object.get('poster', {}).get('slug'))

                args = {"id": int(json_object.get('id')),
                        "gallery_id": int(json_object.get('gallery_id')),
                        "poster": user,
                        "post_date": datetime.fromtimestamp(json_object.get('post_date')).strftime('%Y-%m-%d %H:%M:%S'),
                        "body": json_object.get('body', "")}
                
                return cls(*args.values())

@dataclass
class CommentPage(BaseDataclass):
        total_comments: int
        comments: List[Comment]