import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.domain.entities.manga import Image
from enma.domain.entities.pagination import Thumb
from enma.domain.entities.search_result import SearchResult

class TestSearchResultEntity:

    def test_default_values(self):
        sut = SearchResult(query='teste',
                           page=1,
                           results=[])
        assert sut.results == []
        assert sut.total_pages == 0
        assert sut.total_pages == 0

    def test_set_results_at_instantiation_shouldnt_effect_counters(self):

        thumbs = [Thumb(id='1', url='mocked', title='teste', cover=Image(uri='teste')),
                  Thumb(id='2', url='mocked', title='teste', cover=Image(uri='teste')),
                  Thumb(id='3', url='mocked', title='teste', cover=Image(uri='teste'))]

        sut = SearchResult(query='teste',
                           page=1,
                           results=thumbs)
        
        assert sut.results == thumbs
        assert sut.page == 1
        assert sut.total_results == 0
        assert sut.total_pages == 0
        assert sut.results[0].url == 'mocked'

    def test_set_results_at_instantiation_shouldnt_effect_counters_after(self):

        thumbs = [Thumb(id='1', url='mocked', title='teste', cover=Image(uri='teste')),
                  Thumb(id='2', url='mocked', title='teste', cover=Image(uri='teste')),
                  Thumb(id='3', url='mocked', title='teste', cover=Image(uri='teste'))]

        sut = SearchResult(query='teste',
                           page=1,
                           total_pages=100,
                           total_results=300,
                           results=thumbs)
        
        assert sut.results == thumbs
        assert sut.page == 1
        assert sut.total_results == 300
        assert sut.total_pages == 100
