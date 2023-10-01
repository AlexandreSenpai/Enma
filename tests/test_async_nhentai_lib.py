import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.core.handler import ApiError
from enma.asynch.infra.entrypoints.lib import NHentaiAsync 
from enma.core.interfaces import Doujin, Sort, SearchResult, PopularPage, Page, CommentPage

class TestGetDoujin:
    @pytest.mark.asyncio
    async def test_success_doujin_retrieve(self):
        sut = NHentaiAsync()
        doujin = await sut.get_doujin(doujin_id=1)
        assert doujin.id is not None
        assert isinstance(doujin.id, int)
    
    @pytest.mark.asyncio
    async def test_page_array_matches_with_page_count(self):
        sut = NHentaiAsync()
        doujin = await sut.get_doujin(doujin_id=1)
        assert len(doujin.images) == doujin.total_pages
    
    @pytest.mark.asyncio
    async def test_get_doujin_returns_doujin_instance(self):
        sut = NHentaiAsync()
        doujin = await sut.get_doujin(doujin_id=2)
        assert isinstance(doujin, Doujin)
    
    @pytest.mark.asyncio
    async def test_it_should_throw_error_if_it_doesnt_exists(self):
        sut = NHentaiAsync()
        try:
            await sut.get_doujin(doujin_id=0)
            assert False
        except ApiError as e:
            assert e.status_code == 404

class TestSearchDoujin:
    @pytest.mark.asyncio
    async def test_success_doujin_searching_with_complex_query(self):
        sut = NHentaiAsync()
        search = await sut.search(query='footjob -"incest" -"rape" -"lolicon" -"shotacon"', page=1, sort=Sort.RECENT)
        assert search is not None
        assert len(search.doujins) is not None
        assert len(search.doujins) > 0
    
    @pytest.mark.asyncio
    async def test_success_doujin_searching_with_simple_query(self):
        sut = NHentaiAsync()
        search = await sut.search(query='naruto', page=1, sort=Sort.RECENT)
        assert search is not None
        assert isinstance(search, SearchResult)
        assert len(search.doujins) > 0
        assert True if len(search.doujins) <= 25 and len(search.doujins) == search.total_results else len(search.doujins) == 25 

class TestRandom:
    @pytest.mark.asyncio
    async def test_successfully_get_random(self):
        sut = NHentaiAsync()
        doujin = await sut.get_random()
        
        assert doujin is not None
        assert isinstance(doujin, Doujin)

class TestPopularNow:
    @pytest.mark.asyncio
    async def test_successfully_get_popular_now(self):
        sut = NHentaiAsync()
        popular = await sut.get_popular_now()
        
        assert popular is not None
        assert isinstance(popular, PopularPage)
        assert isinstance(popular.doujins[0], Doujin)