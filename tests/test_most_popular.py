import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NHentai import NHentai
from NHentai import NHentaiAsync
from NHentai.entities.doujin import DoujinThumbnail
from NHentai.entities.page import PopularPage

def test_if_returned_payload_has_all_required_keys():
    doujin = NHentai().get_popular_now()
    for d in doujin.doujins:
        assert d.id is not None
        assert d.cover is not None
        assert d.url is not None
        assert d.tags is not None
        assert d.media_id is not None
        assert d.title is not None
        assert d.languages is not None

def test_if_returned_doujin_instance_belongs_to_DoujinThumbnail():
    doujins = NHentai().get_popular_now()
    for doujin in doujins.doujins:
        assert isinstance(doujin, DoujinThumbnail)

def test_if_returned_instance_belongs_to_PopularPage():
    doujin = NHentai().get_popular_now()
    assert isinstance(doujin, PopularPage)

@pytest.mark.asyncio
async def test_async_case01():
    doujin = await NHentaiAsync().get_popular_now()
    for d in doujin.doujins:
        assert d.id is not None
        assert d.cover is not None
        assert d.url is not None
        assert d.tags is not None
        assert d.media_id is not None
        assert d.title is not None
        assert d.languages is not None

# @pytest.mark.asyncio
# async def test_async_case02():
#     doujins = await NHentaiAsync().get_popular_now()
#     for doujin in doujins.doujins:
#         assert isinstance(doujin, DoujinThumbnail)

# @pytest.mark.asyncio
# async def test_async_case03():
#     doujin = await NHentaiAsync().get_popular_now()
#     assert isinstance(doujin, PopularPage)

