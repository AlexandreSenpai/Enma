import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from NHentai.core.handler import ApiError
from NHentai.sync.infra.entrypoints.lib import NHentai
from NHentai.core.interfaces import Doujin, Sort, SearchResult, PopularPage, Page, CommentPage

class TestGetDoujin:
    def test_success_doujin_retrieve(self):
        sut = NHentai()
        doujin = sut.get_doujin(doujin_id=1)
        assert doujin.id is not None
        assert isinstance(doujin.id, int)
    
    def test_page_array_matches_with_page_count(self):
        sut = NHentai()
        doujin = sut.get_doujin(doujin_id=1)
        assert len(doujin.images) == doujin.total_pages
    
    def test_get_doujin_returns_doujin_instance(self):
        sut = NHentai()
        doujin = sut.get_doujin(doujin_id=2)
        assert isinstance(doujin, Doujin)
    
    def test_it_should_throw_error_if_it_doesnt_exists(self):
        sut = NHentai()
        try:
            sut.get_doujin(doujin_id=0)
            assert False
        except ApiError as e:
            assert e.status_code == 404

class TestSearchDoujin:
    def test_success_doujin_searching_with_complex_query(self):
        sut = NHentai()
        search = sut.search(query='footjob -"incest" -"rape" -"lolicon" -"shotacon"', page=1, sort=Sort.RECENT)
        assert search is not None
        assert len(search.doujins) is not None
        assert len(search.doujins) > 0
    
    def test_success_doujin_searching_with_simple_query(self):
        sut = NHentai()
        search = sut.search(query='naruto', page=1, sort=Sort.RECENT)
        assert search is not None
        assert isinstance(search, SearchResult)
        assert len(search.doujins) > 0
        assert True if len(search.doujins) <= 25 and len(search.doujins) == search.total_results else len(search.doujins) == 25 

class TestRandom:
    def test_successfully_get_random(self):
        sut = NHentai()
        doujin = sut.get_random()
        
        assert doujin is not None
        assert isinstance(doujin, Doujin)

class TestPopularNow:
    def test_successfully_get_popular_now(self):
        sut = NHentai()
        popular = sut.get_popular_now()
        
        assert popular is not None
        assert isinstance(popular, PopularPage)
        assert isinstance(popular.doujins[0], Doujin)
