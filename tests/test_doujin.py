import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NHentai.nhentai import NHentai
from NHentai.nhentai_async import NHentaiAsync

def test_standard_case01():
    doujin = NHentai().get_doujin('320165')
    assert doujin is not None

def test_standard_case02():
    doujin = NHentai().get_doujin('320066')
    assert doujin is not None

def test_standard_case03():
    doujin = NHentai().get_doujin('320067')
    assert doujin is not None

def test_standard_case04():
    doujin = NHentai().get_doujin('0656654654')
    assert doujin is None

def test_standard_case05():
    doujin = NHentai().get_doujin('1212145487')
    assert doujin is None

def test_standard_case06():
    doujin = NHentai().get_doujin('320290')
    assert doujin is not None

def test_standard_case07():
    doujin = NHentai().get_doujin('full color')
    assert doujin is None

def test_standard_case08():
    doujin = NHentai().get_doujin('342490')
    assert doujin.artists is not None
    assert doujin.categories is not None
    assert doujin.groups is not None
    assert doujin.id is not None
    assert doujin.images is not None
    assert doujin.languages is not None
    assert doujin.parodies is not None
    assert doujin.secondary_title is not None
    assert doujin.title is not None
    assert doujin.total_pages is not None

@pytest.mark.asyncio
async def test_async_case01():
    doujin = await NHentaiAsync().get_doujin('320165')
    assert doujin is not None

@pytest.mark.asyncio
async def test_async_case02():
    doujin = await NHentaiAsync().get_doujin('320066')
    assert doujin is not None

@pytest.mark.asyncio
async def test_async_case03():
    doujin = await NHentaiAsync().get_doujin('320067')
    assert doujin is not None

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
    assert doujin is not None

@pytest.mark.asyncio
async def test_async_case07():
    doujin = await NHentaiAsync().get_doujin('full color')
    assert doujin is None

@pytest.mark.asyncio
async def test_async_case08():
    doujin = await NHentaiAsync().get_doujin('342490')
    assert doujin.artists is not None
    assert doujin.categories is not None
    assert doujin.groups is not None
    assert doujin.id is not None
    assert doujin.images is not None
    assert doujin.languages is not None
    assert doujin.parodies is not None
    assert doujin.secondary_title is not None
    assert doujin.title is not None
    assert doujin.total_pages is not None