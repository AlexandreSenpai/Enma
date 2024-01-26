from typing import Literal, TypedDict, Union


class NHentaiImage(TypedDict):
    t: Union[Literal["j"], Literal["p"], Literal["g"]]
    w: int
    h: int
    
class NHentaiImages(TypedDict):
    pages: list[NHentaiImage]
    cover: NHentaiImage
    thumbnail: NHentaiImage

class Title(TypedDict):
    english: str
    japanese: str
    pretty: str

class Tag(TypedDict):
    id: int
    type: str
    name: str
    url: str
    count: int

class NHentaiResponse(TypedDict):
    id: int
    media_id: str
    title: Title
    images: NHentaiImages
    scanlator: str
    upload_date: int
    tags: list[Tag]
    num_pages: int
    num_favorites: int