import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NHentai.nhentai import NHentai
from NHentai.nhentai_async import NHentaiAsync
from NHentai.entities.doujin import DoujinThumbnail
from NHentai.entities.page import PopularPage

def test_standard_case01():
    doujin = NHentai().get_popular_now()
    assert doujin is not None

def test_standard_case02():
    doujins = NHentai().get_popular_now()
    for doujin in doujins.doujins:
        assert isinstance(doujin, DoujinThumbnail)

def test_standard_case03():
    doujin = NHentai().get_popular_now()
    assert isinstance(doujin, PopularPage)

@pytest.mark.asyncio
async def test_async_case01():
    doujin = await NHentaiAsync().get_popular_now()
    assert doujin is not None

@pytest.mark.asyncio
async def test_async_case02():
    doujins = await NHentaiAsync().get_popular_now()
    for doujin in doujins.doujins:
        assert isinstance(doujin, DoujinThumbnail)

@pytest.mark.asyncio
async def test_async_case03():
    doujin = await NHentaiAsync().get_popular_now()
    assert isinstance(doujin, PopularPage)

