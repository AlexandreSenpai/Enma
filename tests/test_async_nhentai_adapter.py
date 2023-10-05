import pytest
import sys
import os

import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.core.handler import ApiError
from enma.core.interfaces import Cover, Doujin, DoujinPage, Tag, Sort, Page, CommentPage, Comment
from enma.asynch.infra.adapters.repositories.hentai.implementations.nhentai import NHentaiAdapter
from enma.asynch.infra.adapters.request.http.implementations.asynk import RequestsAdapter

class TestGetDoujin:
    @pytest.mark.asyncio
    async def test_get_doujin_successfully(self):
        sut = NHentaiAdapter(RequestsAdapter())
        doujin = await sut.get_doujin(doujin_id=279406)

        assert doujin.id == 279406
    
    @pytest.mark.asyncio
    async def test_it_should_throw_exception_when_doujin_was_not_found(self):
        sut = NHentaiAdapter(RequestsAdapter())
        try:
            await sut.get_doujin(doujin_id=0)
            assert False
        except ApiError as e:
            assert e.status_code == 404
            
    @pytest.mark.asyncio
    async def test_get_doujin_successfully_passing_string_id(self):
        sut = NHentaiAdapter(RequestsAdapter())
        doujin = await sut.get_doujin(doujin_id='279406')

        assert doujin.id == 279406
    
    @pytest.mark.asyncio
    async def test_get_doujin_response_instance(self):
        sut = NHentaiAdapter(RequestsAdapter())
        doujin = await sut.get_doujin(doujin_id=279406)

        assert isinstance(doujin, Doujin)
    
    @pytest.mark.asyncio
    async def test_get_doujin_should_not_have_none_fields(self):
        sut = NHentaiAdapter(RequestsAdapter())
        doujin = await sut.get_doujin(doujin_id=279406)

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
        
    @pytest.mark.asyncio
    async def test_doujin_pages_url_should_exist(self):
        sut = NHentaiAdapter(RequestsAdapter())
        doujin = await sut.get_doujin(doujin_id=216581)
        req = requests.get(doujin.images[0].src)
        assert req.status_code == 200

class TestSearchDoujin:
    @pytest.mark.asyncio
    async def test_searching_doujin_successfully_excluding_tags(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = await sut.search_doujin(search_term='esdeath -lolicon -shotacon -incest -rape')
        
        assert searching_result is not None
        assert searching_result.doujins is not None and False not in [isinstance(doujin, Doujin) for doujin in searching_result.doujins]
        assert searching_result.total_pages is not None and searching_result.total_pages > 0
        assert searching_result.total_results == len(searching_result.doujins) if searching_result.total_pages == 1 else False

    @pytest.mark.asyncio
    async def test_searching_doujin_successfully(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = await sut.search_doujin(search_term='araragi')

        assert searching_result is not None
        assert searching_result.doujins is not None and False not in [isinstance(doujin, Doujin) for doujin in searching_result.doujins]
        assert searching_result.total_pages is not None and searching_result.total_pages > 0
    
    @pytest.mark.asyncio
    async def test_searching_with_custom_sort(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = await sut.search_doujin(search_term='houshou marine', sort=Sort.WEEK)

        assert searching_result is not None
        assert searching_result.doujins is not None and False not in [isinstance(doujin, Doujin) for doujin in searching_result.doujins]
        assert searching_result.sort == 'popular-week'
  
    @pytest.mark.asyncio
    async def test_searching_with_no_results(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = await sut.search_doujin(search_term='alexandresenpai')

        assert searching_result is not None
        assert searching_result.doujins == []
        assert searching_result.total_pages == 1
        assert searching_result.total_results == 0
  
    @pytest.mark.asyncio
    async def test_searching_paginating(self):
        sut = NHentaiAdapter(RequestsAdapter())
        searching_result = await sut.search_doujin(search_term='houshou marine', page=2)

        assert searching_result is not None
        assert searching_result.doujins is not None and False not in [isinstance(doujin, Doujin) for doujin in searching_result.doujins]
        assert searching_result.page == 2

class TestGetComments:
    @pytest.mark.asyncio
    async def test_it_should_get_all_comments_successfully(self):
        sut = NHentaiAdapter(RequestsAdapter())
        comments = await sut.get_comments(doujin_id=216581)
        assert isinstance(comments, CommentPage)
        assert len(comments.comments) == comments.total_comments
        assert isinstance(comments.comments[0], Comment)
    
    @pytest.mark.asyncio
    async def test_it_should_throw_error_when_it_doesnt_find_comments(self):
        sut = NHentaiAdapter(RequestsAdapter())
        try:
            await sut.get_comments(doujin_id=0)
            assert False
        except ApiError as err:
            assert err.status_code == 404
    
    @pytest.mark.asyncio
    async def test_avatar_url_should_exist(self):
        sut = NHentaiAdapter(RequestsAdapter())
        comments = await sut.get_comments(doujin_id=216581)
        req = requests.get(comments.comments[0].poster.avatar_url)
        assert req.status_code == 200

class TestGetPage:
    @pytest.mark.asyncio
    async def test_it_should_get_first_page_successfully(self):
        sut = NHentaiAdapter(RequestsAdapter())
        page = await sut.get_page(page=1)
        assert isinstance(page, Page)
        assert isinstance(page.doujins[0], Doujin)
    
    @pytest.mark.asyncio
    async def test_it_should_throw_error_when_it_doesnt_find_page(self):
        sut = NHentaiAdapter(RequestsAdapter())
        page = await sut.get_page(page=-10)
        assert len(page.doujins) == 0
