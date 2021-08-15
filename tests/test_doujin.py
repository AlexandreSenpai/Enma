from datetime import datetime
import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NHentai import NHentai
from NHentai import NHentaiAsync
from NHentai.entities.doujin import Doujin, DoujinPage, Tag, Title

def test_standard_specting_doujin_00():
    doujin = NHentai().get_doujin('320165')

    assert doujin.artists is not None and False not in [isinstance(tag, Tag) for tag in doujin.artists]
    assert doujin.upload_at is not None and isinstance(doujin.upload_at, datetime)
    assert doujin.categories is not None and False not in [isinstance(tag, Tag) for tag in doujin.categories]
    assert doujin.groups is not None and False not in [isinstance(tag, Tag) for tag in doujin.groups]
    assert doujin.id is not None and isinstance(doujin.id, int)
    assert doujin.images is not None and False not in [isinstance(image, DoujinPage) for image in doujin.images]
    assert doujin.languages is not None and False not in [isinstance(tag, Tag) for tag in doujin.languages]
    assert doujin.parodies is not None and False not in [isinstance(tag, Tag) for tag in doujin.parodies]
    assert doujin.title is not None and isinstance(doujin.title, Title)
    assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)
    assert doujin is not None and isinstance(doujin, Doujin)

def test_standard_specting_doujin_01():
    doujin = NHentai().get_doujin('320066')

    assert doujin.artists is not None and False not in [isinstance(tag, Tag) for tag in doujin.artists]
    assert doujin.upload_at is not None and isinstance(doujin.upload_at, datetime)
    assert doujin.categories is not None and False not in [isinstance(tag, Tag) for tag in doujin.categories]
    assert doujin.groups is not None and False not in [isinstance(tag, Tag) for tag in doujin.groups]
    assert doujin.id is not None and isinstance(doujin.id, int)
    assert doujin.images is not None and False not in [isinstance(image, DoujinPage) for image in doujin.images]
    assert doujin.languages is not None and False not in [isinstance(tag, Tag) for tag in doujin.languages]
    assert doujin.parodies is not None and False not in [isinstance(tag, Tag) for tag in doujin.parodies]
    assert doujin.title is not None and isinstance(doujin.title, Title)
    assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)
    assert doujin is not None and isinstance(doujin, Doujin)

def test_standard_specting_doujin_02():
    doujin = NHentai().get_doujin('320067')
    
    assert doujin.artists is not None and False not in [isinstance(tag, Tag) for tag in doujin.artists]
    assert doujin.upload_at is not None and isinstance(doujin.upload_at, datetime)
    assert doujin.categories is not None and False not in [isinstance(tag, Tag) for tag in doujin.categories]
    assert doujin.groups is not None and False not in [isinstance(tag, Tag) for tag in doujin.groups]
    assert doujin.id is not None and isinstance(doujin.id, int)
    assert doujin.images is not None and False not in [isinstance(image, DoujinPage) for image in doujin.images]
    assert doujin.languages is not None and False not in [isinstance(tag, Tag) for tag in doujin.languages]
    assert doujin.parodies is not None and False not in [isinstance(tag, Tag) for tag in doujin.parodies]
    assert doujin.title is not None and isinstance(doujin.title, Title)
    assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)
    assert doujin is not None and isinstance(doujin, Doujin)

def test_standard_specting_doujin_03():
    doujin = NHentai().get_doujin('320290')

    assert doujin.artists is not None and False not in [isinstance(tag, Tag) for tag in doujin.artists]
    assert doujin.upload_at is not None and isinstance(doujin.upload_at, datetime)
    assert doujin.categories is not None and False not in [isinstance(tag, Tag) for tag in doujin.categories]
    assert doujin.groups is not None and False not in [isinstance(tag, Tag) for tag in doujin.groups]
    assert doujin.id is not None and isinstance(doujin.id, int)
    assert doujin.images is not None and False not in [isinstance(image, DoujinPage) for image in doujin.images]
    assert doujin.languages is not None and False not in [isinstance(tag, Tag) for tag in doujin.languages]
    assert doujin.parodies is not None and False not in [isinstance(tag, Tag) for tag in doujin.parodies]
    assert doujin.title is not None and isinstance(doujin.title, Title)
    assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)
    assert doujin is not None and isinstance(doujin, Doujin)

def test_standard_not_specting_doujin_00():
    doujin = NHentai().get_doujin('0656654654')
    assert doujin is None

def test_standard_not_specting_doujin_01():
    doujin = NHentai().get_doujin('1212145487')
    assert doujin is None

def test_standard_not_specting_doujin_02():
    doujin = NHentai().get_doujin('full color')
    assert doujin is None

@pytest.mark.asyncio
async def test_async_case01():
    doujin = await NHentaiAsync().get_doujin('320165')
    
    assert doujin.artists is not None and False not in [isinstance(tag, Tag) for tag in doujin.artists]
    assert doujin.upload_at is not None and isinstance(doujin.upload_at, datetime)
    assert doujin.categories is not None and False not in [isinstance(tag, Tag) for tag in doujin.categories]
    assert doujin.groups is not None and False not in [isinstance(tag, Tag) for tag in doujin.groups]
    assert doujin.id is not None and isinstance(doujin.id, int)
    assert doujin.images is not None and False not in [isinstance(image, DoujinPage) for image in doujin.images]
    assert doujin.languages is not None and False not in [isinstance(tag, Tag) for tag in doujin.languages]
    assert doujin.parodies is not None and False not in [isinstance(tag, Tag) for tag in doujin.parodies]
    assert doujin.title is not None and isinstance(doujin.title, Title)
    assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)
    assert doujin is not None and isinstance(doujin, Doujin)

@pytest.mark.asyncio
async def test_async_case02():
    doujin = await NHentaiAsync().get_doujin('320066')
    
    assert doujin.artists is not None and False not in [isinstance(tag, Tag) for tag in doujin.artists]
    assert doujin.upload_at is not None and isinstance(doujin.upload_at, datetime)
    assert doujin.categories is not None and False not in [isinstance(tag, Tag) for tag in doujin.categories]
    assert doujin.groups is not None and False not in [isinstance(tag, Tag) for tag in doujin.groups]
    assert doujin.id is not None and isinstance(doujin.id, int)
    assert doujin.images is not None and False not in [isinstance(image, DoujinPage) for image in doujin.images]
    assert doujin.languages is not None and False not in [isinstance(tag, Tag) for tag in doujin.languages]
    assert doujin.parodies is not None and False not in [isinstance(tag, Tag) for tag in doujin.parodies]
    assert doujin.title is not None and isinstance(doujin.title, Title)
    assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)
    assert doujin is not None and isinstance(doujin, Doujin)

@pytest.mark.asyncio
async def test_async_case03():
    doujin = await NHentaiAsync().get_doujin('320067')
    
    assert doujin.artists is not None and False not in [isinstance(tag, Tag) for tag in doujin.artists]
    assert doujin.upload_at is not None and isinstance(doujin.upload_at, datetime)
    assert doujin.categories is not None and False not in [isinstance(tag, Tag) for tag in doujin.categories]
    assert doujin.groups is not None and False not in [isinstance(tag, Tag) for tag in doujin.groups]
    assert doujin.id is not None and isinstance(doujin.id, int)
    assert doujin.images is not None and False not in [isinstance(image, DoujinPage) for image in doujin.images]
    assert doujin.languages is not None and False not in [isinstance(tag, Tag) for tag in doujin.languages]
    assert doujin.parodies is not None and False not in [isinstance(tag, Tag) for tag in doujin.parodies]
    assert doujin.title is not None and isinstance(doujin.title, Title)
    assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)
    assert doujin is not None and isinstance(doujin, Doujin)

@pytest.mark.asyncio
async def test_async_case04():
    doujin = await NHentaiAsync().get_doujin('0656654654')
    assert doujin is None

@pytest.mark.asyncio
async def test_async_case05():
    doujin = await NHentaiAsync().get_doujin('1212145487')
    assert doujin is None

@pytest.mark.asyncio
async def test_async_case06():
    doujin = await NHentaiAsync().get_doujin('320290')
    
    assert doujin.artists is not None and False not in [isinstance(tag, Tag) for tag in doujin.artists]
    assert doujin.upload_at is not None and isinstance(doujin.upload_at, datetime)
    assert doujin.categories is not None and False not in [isinstance(tag, Tag) for tag in doujin.categories]
    assert doujin.groups is not None and False not in [isinstance(tag, Tag) for tag in doujin.groups]
    assert doujin.id is not None and isinstance(doujin.id, int)
    assert doujin.images is not None and False not in [isinstance(image, DoujinPage) for image in doujin.images]
    assert doujin.languages is not None and False not in [isinstance(tag, Tag) for tag in doujin.languages]
    assert doujin.parodies is not None and False not in [isinstance(tag, Tag) for tag in doujin.parodies]
    assert doujin.title is not None and isinstance(doujin.title, Title)
    assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)
    assert doujin is not None and isinstance(doujin, Doujin)

@pytest.mark.asyncio
async def test_async_case07():
    doujin = await NHentaiAsync().get_doujin('full color')
    assert doujin is None

@pytest.mark.asyncio
async def test_async_case08():
    doujin = await NHentaiAsync().get_doujin('342490')

    assert doujin.artists is not None and False not in [isinstance(tag, Tag) for tag in doujin.artists]
    assert doujin.upload_at is not None and isinstance(doujin.upload_at, datetime)
    assert doujin.categories is not None and False not in [isinstance(tag, Tag) for tag in doujin.categories]
    assert doujin.groups is not None and False not in [isinstance(tag, Tag) for tag in doujin.groups]
    assert doujin.id is not None and isinstance(doujin.id, int)
    assert doujin.images is not None and False not in [isinstance(image, DoujinPage) for image in doujin.images]
    assert doujin.languages is not None and False not in [isinstance(tag, Tag) for tag in doujin.languages]
    assert doujin.parodies is not None and False not in [isinstance(tag, Tag) for tag in doujin.parodies]
    assert doujin.title is not None and isinstance(doujin.title, Title)
    assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)
    assert doujin is not None and isinstance(doujin, Doujin)