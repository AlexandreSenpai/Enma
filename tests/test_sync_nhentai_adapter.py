import pytest
import sys
import os
from enma.core.handler import ApiError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.core.interfaces import Cover, Doujin, DoujinPage, Tag, Sort, Page, CommentPage
from enma.sync.infra.adapters.repositories.hentai.implementations.nhentai import NHentaiAdapter
from enma.sync.infra.adapters.request.http.implementations.sync import RequestsAdapter

class TestGetDoujin:
    def test_get_doujin_successfully(self):
        sut = NHentaiAdapter(RequestsAdapter())
        doujin = sut.get_doujin(doujin_id=279406)

        assert doujin.id == 279406
    
    def test_it_should_throw_exception_when_doujin_was_not_found(self):
        sut = NHentaiAdapter(RequestsAdapter())
        try:
            sut.get_doujin(doujin_id=0)
            assert False
        except ApiError as e:
            assert e.status_code == 404
            
    def test_get_doujin_successfully_passing_string_id(self):
        sut = NHentaiAdapter(RequestsAdapter())
        doujin = sut.get_doujin(doujin_id='279406')

        assert doujin.id == 279406
    
    def test_get_doujin_response_instance(self):
        sut = NHentaiAdapter(RequestsAdapter())
        doujin = sut.get_doujin(doujin_id=279406)

        assert isinstance(doujin, Doujin)
    
    def test_get_doujin_should_not_have_none_fields(self):
        sut = NHentaiAdapter(RequestsAdapter())
        doujin = sut.get_doujin(doujin_id=279406)

        assert doujin.id == 279406
        assert doujin.title.english is not None and isinstance(doujin.title.english, str)
        assert doujin.title.japanese is not None and isinstance(doujin.title.japanese, str)
        assert doujin.title.pretty is not None and isinstance(doujin.title.pretty, str)
        assert doujin.media_id is not None and isinstance(doujin.media_id, int)
        assert doujin.upload_at is not None and isinstance(doujin.upload_at, str)
        assert doujin.url is not None and isinstance(doujin.url, str)
        assert doujin.tags is not None and not False in [isinstance(tag, Tag) for tag in doujin.tags]
        assert doujin.artists is not None and not False in [isinstance(tag, Tag) for tag in doujin.artists]
        assert doujin.languages is not None and not False in [isinstance(tag, Tag) for tag in doujin.languages]
        assert doujin.categories is not None and not False in [isinstance(tag, Tag) for tag in doujin.categories]
        assert doujin.characters is not None and not False in [isinstance(tag, Tag) for tag in doujin.characters]
        assert doujin.parodies is not None and not False in [isinstance(tag, Tag) for tag in doujin.parodies]
        assert doujin.groups is not None and not False in [isinstance(tag, Tag) for tag in doujin.groups]
        assert doujin.cover is not None and isinstance(doujin.cover, Cover)
        assert doujin.images is not None and [isinstance(image, DoujinPage) for image in doujin.images]
        assert doujin.total_favorites is not None and isinstance(doujin.total_favorites, int)
        assert doujin.total_pages is not None and isinstance(doujin.total_pages, int)

class TestSearchDoujin:
    def test_searching_doujin_successfully_excluding_tags(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = sut.search_doujin(search_term='esdeath -lolicon -shotacon -incest -rape')
        
        assert searching_result is not None
        assert searching_result.doujins is not None and False not in [isinstance(doujin, Doujin) for doujin in searching_result.doujins]
        assert searching_result.total_pages is not None and searching_result.total_pages > 0

    def test_searching_doujin_successfully(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = sut.search_doujin(search_term='araragi')

        assert searching_result is not None
        assert searching_result.doujins is not None and False not in [isinstance(doujin, Doujin) for doujin in searching_result.doujins]
        assert searching_result.total_pages is not None and searching_result.total_pages > 0
    
    def test_searching_with_custom_sort(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = sut.search_doujin(search_term='houshou marine', sort=Sort.WEEK)

        assert searching_result is not None
        assert searching_result.doujins is not None and False not in [isinstance(doujin, Doujin) for doujin in searching_result.doujins]
        assert searching_result.sort == 'popular-week'
  
    def test_searching_with_no_results(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = sut.search_doujin(search_term='alexandresenpai')

        assert searching_result is not None
        assert searching_result.doujins == []
        assert searching_result.total_pages == 1
        assert searching_result.total_results == 0
  
    def test_searching_paginating(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = sut.search_doujin(search_term='houshou marine', page=2)

        assert searching_result is not None
        assert searching_result.doujins is not None and False not in [isinstance(doujin, Doujin) for doujin in searching_result.doujins]
        assert searching_result.sort is None
        assert searching_result.page == 2
        