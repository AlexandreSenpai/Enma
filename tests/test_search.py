import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NHentai.nhentai import NHentai
from NHentai.nhentai_async import NHentaiAsync

def test_standard_case01():
    search = NHentai().search('320165')
    assert search is not None

def test_standard_case02():
    search = NHentai().search('658468468')
    assert len(search.doujins) == 0

def test_standard_case03():
    search = NHentai().search('naruto')
    assert len(search.doujins) > 0

def test_standard_case04():
    search = NHentai().search('320253')
    assert search is not None

def test_standard_case05():
    search = NHentai().search('320066')
    assert search is not None

def test_standard_case06():
    search = NHentai().search('auhdasudhudasd')
    assert len(search.doujins) == 0

def test_standard_case07():
    search = NHentai().search('full color')
    assert len(search.doujins) > 0

@pytest.mark.asyncio
async def test_async_case01():
    search = await NHentaiAsync().search('320165')
    assert search is not None

@pytest.mark.asyncio
async def test_async_case02():
    search = await NHentaiAsync().search('658468468')
    assert len(search.doujins) == 0

@pytest.mark.asyncio
async def test_async_case03():
    search = await NHentaiAsync().search('naruto')
    assert len(search.doujins) > 0

@pytest.mark.asyncio
async def test_async_case04():
    search = await NHentaiAsync().search('320253')
    assert search is not None

@pytest.mark.asyncio
async def test_async_case05():
    search = await NHentaiAsync().search('320066')
    assert search is not None

@pytest.mark.asyncio
async def test_async_case06():
    search = await NHentaiAsync().search('auhdasudhudasd')
    assert len(search.doujins) == 0

@pytest.mark.asyncio
async def test_async_case07():
    search = await NHentaiAsync().search('full color')
    assert len(search.doujins) > 0
