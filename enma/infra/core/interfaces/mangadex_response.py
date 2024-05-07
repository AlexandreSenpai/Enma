from typing import Any, Literal, TypedDict, Union, TypeVar


class Title(TypedDict):
    en: str

class MangaDesc(TypedDict):
    en: str

class TagAttrs(TypedDict):
    name: dict[str, str]
    description: dict[str, str]
    group: Union[Literal["theme"], Literal["genre"], 
                 Literal["format"]]
    version: int

class IMangaTag(TypedDict):
    id: str
    type: str
    attributes: TagAttrs
    relationships: list[Any]

IAltTitles = list[dict[str, str]]

class MangaAttrs(TypedDict):
    title: Title
    altTitles: IAltTitles
    description: MangaDesc
    isLocked: bool
    links: dict[str, str]
    originalLanguage: str
    lastVolume: str
    lastChapter: str
    publicationDemographic: Any
    status: str
    year: int
    contentRating: str
    tags: list[IMangaTag]
    state: str
    chapterNumbersResetOnNewVolume: bool
    createdAt: str
    updatedAt: str
    version: int
    availableTranslatedLanguages: list[str]
    latestUploadedChapter: str

class CoverAttrs(TypedDict):
    description: str
    volume: int
    fileName: str
    locale: str
    createdAt: str
    updatedAt: str
    version: int

class CoverArtRelation(TypedDict):
    id: str
    type: Literal["cover_art"]
    attributes: CoverAttrs

class PersonAttrs(TypedDict):
    name: str
    imageUrl: str
    biography: dict[str, str]
    twitter: str
    pixiv: str
    melonBook: str
    fanBox: str
    booth: str
    namicomi: str
    nicoVideo: str
    skeb: str
    fantia: str
    tumblr: str
    youtube: str
    weibo: str
    naver: str
    website: str
    createdAt: str
    updatedAt: str
    version: int

class AuthorRelation(TypedDict):
    id: str
    type: Union[Literal["author"], Literal["artist"]]
    attributes: PersonAttrs

IRelations = list[Union[CoverArtRelation,
                       AuthorRelation,
                       dict[str, str]]]

class IManga(TypedDict):
    id: str
    type: str
    attributes: MangaAttrs
    relationships: IRelations

class IGetResult(TypedDict):
    result: str
    response: str
    data: IManga

class ISearchResult(IGetResult):
    limit: int
    offset: int
    total: int
    result: str
    response: str
    data: list[IManga]

class IChapter(TypedDict):
    chapter: str
    id: str
    others: list
    count: int

class IVolume(TypedDict):
    volume: str
    count: int
    chapters: dict[str, IChapter]

class IVolumesResponse(TypedDict):
    result: str
    volumes: dict[str, IVolume]

class IChapterHash(TypedDict):
    hash: str
    data: list[str]
    dataSaver: list[str]

class IHash(TypedDict):
    result: str
    baseUrl: str
    chapter: IChapterHash
