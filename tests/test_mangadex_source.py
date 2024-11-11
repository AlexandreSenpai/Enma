import os

from unittest.mock import MagicMock, Mock, patch
import sys

import pytest


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.application.core.handlers.error import Forbidden, NotFound, Unknown
from enma.domain.entities.pagination import Thumb
from enma.infra.adapters.repositories.mangadex import Mangadex
from enma.domain.entities.manga import Author, Chapter, Genre, Image, SymbolicLink

from tests.data.mocked_doujins import mangadex_paginate_mocked

class TestMangadexSourceGetMethod:

    sut = Mangadex()

    def test_success_doujin_retrieve(self):
        
        res = self.sut.get(identifier='65498ee8-3c32-4228-b433-73a4d08f8927', 
                           with_symbolic_links=True)

        assert res is not None
        assert res.id == '65498ee8-3c32-4228-b433-73a4d08f8927'
        assert res.title.english == "Monster Musume no Iru Nichijou"
        assert res.title.japanese == "Monster Musume no Iru Nichijō"
        assert res.title.other != ''
        assert res.url != ''
        
        for genre in res.genres:
            assert isinstance(genre, Genre)
        
        for author in res.authors:
            assert isinstance(author, Author)

        assert isinstance(res.thumbnail, Image)
        assert isinstance(res.cover, Image)

        for chapter in res.chapters:
            assert isinstance(chapter, Chapter)
            assert isinstance(chapter.link, SymbolicLink)

    def test_response_when_it_could_not_get_doujin(self):
        with pytest.raises(NotFound):
            self.sut.get(identifier='manga-kb951984', with_symbolic_links=True)
        
    @patch('requests.get')
    def test_raise_forbidden_in_case_of_403_status_code(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 403
        mock_method.return_value = mock

        with pytest.raises(Forbidden):
            self.sut.get(identifier='manga-kb951984')
            mock_method.assert_called_with(url='https://chapMangadex.com/manga-kb951984', 
                                        headers={'Referer': 'https://chapMangadex.com/'}, 
                                        params={})

    @patch.object(sut, '_Mangadex__list_chapters', autospec=True)
    def test_return_empty_chapters(self, mock_method: MagicMock):
        mock_method.return_value = []

        doujin = self.sut.get(identifier='65498ee8-3c32-4228-b433-73a4d08f8927', 
                              with_symbolic_links=True)
        
        assert doujin is not None

        assert len(doujin.chapters) == 0
        assert doujin.id == '65498ee8-3c32-4228-b433-73a4d08f8927'
        assert doujin.title.english == "Monster Musume no Iru Nichijou"
        assert doujin.title.japanese == "Monster Musume no Iru Nichijō"
        
        for genre in doujin.genres:
            assert isinstance(genre, Genre)
        
        for author in doujin.authors:
            assert isinstance(author, Author)

        assert isinstance(doujin.thumbnail, Image)
        assert isinstance(doujin.cover, Image)
    
    def test_get_with_symbolic_link(self):

            doujin = self.sut.get(identifier='65498ee8-3c32-4228-b433-73a4d08f8927', with_symbolic_links=True)

            assert doujin is not None
            assert isinstance(doujin.chapters[0], Chapter)
            assert doujin.chapters[0].link is not None
            assert doujin.chapters[0].link != ""

class TestMangadexSourcePaginationMethod:
    sut = Mangadex()

    def test_success_pagination(self):
        res = self.sut.paginate(page=2)

        assert res is not None
        assert res.id is not None
        assert res.page == 2
        assert res.total_pages > 0
        assert res.total_results > 0
        assert len(res.results) == 25
        
    @patch('requests.get')
    def test_must_return_empty_search_result(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = mangadex_paginate_mocked
        mock_method.return_value = mock
        
        res = self.sut.paginate(page=2)

        assert res is not None
        assert res.id is not None
        assert res.page == 2
        assert res.total_pages == 0
        assert res.total_results == 0
        assert len(res.results) == 0

    @patch('requests.get')
    def test_response_when_forbidden(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 403
        mock_method.return_value = mock
        
        with pytest.raises(Forbidden):
            self.sut.paginate(page=2)

class TestMangadexSourceSearchMethod:

    sut = Mangadex()

    def test_success_searching(self):

        res = self.sut.search(query='GATE', page=1)

        assert res is not None
        assert res.query == 'GATE'
        assert res.id is not None
        assert res.page == 1
        assert res.total_pages > 0
        assert len(res.results) > 0

        for result in res.results:
            assert isinstance(result, Thumb)
            assert result.cover is not None
            assert isinstance(result.cover, Image)
            assert isinstance(result.cover.width, int)
            assert isinstance(result.cover.height, int)
            assert result.cover.width == 512
            assert result.cover.height == 0
            assert result.title is not None
            assert result.id != 0

    def test_success_searching_using_per_page_param(self):

        res = self.sut.search(query='GATE', page=1, per_page=1)

        assert res is not None
        assert res.query == 'GATE'
        assert res.id is not None
        assert res.page == 1
        assert res.total_pages > 0
        assert len(res.results) == 1

        for result in res.results:
            assert isinstance(result, Thumb)
            assert result.cover is not None
            assert isinstance(result.cover, Image)
            assert isinstance(result.cover.width, int)
            assert isinstance(result.cover.height, int)
            assert result.cover.width == 512
            assert result.cover.height == 0
            assert result.title is not None
            assert result.id != 0
        
    @patch('requests.get')
    def test_response_when_forbidden(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 403
        mock_method.return_value = mock

        with pytest.raises(Forbidden):
            self.sut.search(query='Monster Musume no Iru Nichijou', page=1)
    
    @patch('requests.get')
    def test_response_when_not_found(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 404
        mock_method.return_value = mock

        with pytest.raises(NotFound):
            self.sut.search(query='Monster Musume no Iru Nichijou', page=1)
    
    @patch('requests.get')
    def test_response_when_unknown(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 500
        mock_method.return_value = mock

        with pytest.raises(Unknown):
            self.sut.search(query='Monster Musume no Iru Nichijou', page=1)
