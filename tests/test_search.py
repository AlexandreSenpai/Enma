import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NHentai import NHentai
from NHentai import NHentaiAsync
from NHentai.entities.doujin import Title
from NHentai.entities.options import Sort

def test_standard_normal_query_00():
    search = NHentai().search('naruto')

    assert search is not None
    assert search.query is not None
    assert search.doujins is not None
    assert search.total_pages is not None
    assert search.sort is None
    assert isinstance(search.doujins, list)
    assert isinstance(search.total_pages, int)
    assert isinstance(search.query, str)

def test_standard_normal_query_01():
    search = NHentai().search('full color')

    assert search is not None
    assert search.query is not None
    assert search.doujins is not None
    assert search.total_pages is not None
    assert search.sort is None
    assert isinstance(search.doujins, list)
    assert isinstance(search.total_pages, int)
    assert isinstance(search.query, str)

def test_standard_normal_sort_month():
    month = NHentai().search(query='full color', sort=Sort.MONTH)

    assert month is not None
    assert month.query is not None
    assert month.doujins is not None
    assert month.total_pages is not None
    assert month.sort is not None
    assert isinstance(month.doujins, list)
    assert isinstance(month.sort, str)
    assert isinstance(month.total_pages, int)
    assert isinstance(month.query, str)

def test_standard_normal_sort_week():
    week = NHentai().search(query='full color', sort=Sort.WEEK)

    assert week is not None
    assert week.query is not None
    assert week.doujins is not None
    assert week.total_pages is not None
    assert week.sort is not None
    assert isinstance(week.doujins, list)
    assert isinstance(week.sort, str)
    assert isinstance(week.total_pages, int)
    assert isinstance(week.query, str)
    
def test_standard_normal_sort_today():
    today = NHentai().search(query='full color', sort=Sort.TODAY)

    assert today is not None
    assert today.query is not None
    assert today.doujins is not None
    assert today.total_pages is not None
    assert today.sort is not None
    assert isinstance(today.doujins, list)
    assert isinstance(today.sort, str)
    assert isinstance(today.total_pages, int)
    assert isinstance(today.query, str)

def test_standard_normal_sort_all_time():
    all_time = NHentai().search(query='full color', sort=Sort.ALL_TIME)

    assert all_time is not None
    assert all_time.query is not None
    assert all_time.doujins is not None
    assert all_time.total_pages is not None
    assert all_time.sort is not None
    assert isinstance(all_time.doujins, list)
    assert isinstance(all_time.sort, str)
    assert isinstance(all_time.total_pages, int)
    assert isinstance(all_time.query, str)

def test_standard_no_findings_00():
    search = NHentai().search('658468468')

    assert len(search.doujins) == 0
    assert search.total_results == 0
    assert search.total_pages == 0

def test_standard_no_findings_01():
    search = NHentai().search('auhdasudhudasd')

    assert len(search.doujins) == 0
    assert search.total_results == 0
    assert search.total_pages == 0

def test_standard_direct_id_00():
    search = NHentai().search('320253')

    assert search.artists is not None
    assert search.categories is not None
    assert search.groups is not None
    assert search.id is not None
    assert search.images is not None
    assert search.languages is not None
    assert search.parodies is not None
    assert search.title is not None
    assert search.total_pages is not None
    assert isinstance(search.title, Title)

def test_standard_direct_id_01():
    search = NHentai().search('320066')

    assert search.artists is not None
    assert search.categories is not None
    assert search.groups is not None
    assert search.id is not None
    assert search.images is not None
    assert search.languages is not None
    assert search.parodies is not None
    assert search.title is not None
    assert search.total_pages is not None
    assert isinstance(search.title, Title)

@pytest.mark.asyncio
async def test_async_instance_check():
    search = await NHentaiAsync().search('naruto')
    
    assert search is not None
    assert search.query is not None
    assert search.doujins is not None
    assert search.total_pages is not None
    assert search.sort is None
    assert isinstance(search.doujins, list)
    assert isinstance(search.total_pages, int)
    assert isinstance(search.query, str)

@pytest.mark.asyncio
async def test_async_no_findings_00():
    search = await NHentaiAsync().search('658468468')

    assert len(search.doujins) == 0
    assert search.total_results == 0
    assert search.total_pages == 0

@pytest.mark.asyncio
async def test_async_no_findings_01():
    search = await NHentaiAsync().search('21312322231')

    assert len(search.doujins) == 0
    assert search.total_results == 0
    assert search.total_pages == 0

@pytest.mark.asyncio
async def test_async_direct_id_00():
    search = await NHentaiAsync().search('320253')
    
    assert search.artists is not None
    assert search.categories is not None
    assert search.groups is not None
    assert search.id is not None
    assert search.images is not None
    assert search.languages is not None
    assert search.parodies is not None
    assert search.title is not None
    assert search.total_pages is not None
    assert isinstance(search.title, Title)

@pytest.mark.asyncio
async def test_async_direct_id_01():
    search = await NHentaiAsync().search('320066')

    assert search is not None
    assert search.artists is not None
    assert search.categories is not None
    assert search.groups is not None
    assert search.id is not None
    assert search.images is not None
    assert search.languages is not None
    assert search.parodies is not None
    assert search.title is not None
    assert search.total_pages is not None
    assert isinstance(search.title, Title)
