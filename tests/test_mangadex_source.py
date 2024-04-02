from unittest.mock import MagicMock, Mock, patch
import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.application.core.handlers.error import Forbidden, NotFound, Unknown
from enma.domain.entities.pagination import Thumb
from enma.infra.adapters.repositories.mangadex import Mangadex
from enma.domain.entities.manga import MIME, Author, Chapter, Genre, Image, SymbolicLink

class TestMangadexSourceGetMethod:

    sut = Mangadex()

    def test_success_doujin_retrieve(self):
        
        res = self.sut.get(identifier='65498ee8-3c32-4228-b433-73a4d08f8927', with_symbolic_links=True)

        assert res is not None
        assert res.id == '65498ee8-3c32-4228-b433-73a4d08f8927'
        assert res.title.english == "Monster Musume No Iru Nichijou"
        assert res.title.japanese == "モンスター娘のいる日常"
        assert res.title.other == "魔物娘的同居日常"
        
        for genre in res.genres:
            assert isinstance(genre, Genre)
        
        for author in res.authors:
            assert isinstance(author, Author)

        assert isinstance(res.thumbnail, Image)
        assert isinstance(res.cover, Image)

        for chapter in res.chapters:
            assert isinstance(chapter, Chapter)
            assert isinstance(chapter.link, SymbolicLink)

    # def test_response_when_it_could_not_get_doujin(self):
    #     doujin = self.sut.get(identifier='manga-kb951984', with_symbolic_links=True)
        
    #     assert doujin is None
    
#     @patch('requests.get')
#     def test_return_none_when_not_receive_200_status_code(self, mock_method: MagicMock):
#             mock = Mock()
#             mock.status_code = 403
#             mock_method.return_value = mock

#             doujin = self.sut.get(identifier='manga-kb951984')

#             assert doujin is None
#             mock_method.assert_called_with(url='https://chapMangadex.com/manga-kb951984', 
#                                            headers={'Referer': 'https://chapMangadex.com/'}, 
#                                            params={})
    
#     @patch('requests.get')
#     def test_return_empty_chapters(self, mock_method: MagicMock):
#         mock = Mock()
#         mock.status_code = 200
#         mock.text = Mangadex_manga_page_empty_chapters_mocked

#         mock_method.return_value = mock

#         doujin = self.sut.get(identifier='manga-kb951984')

#         assert doujin is not None
#         assert len(doujin.chapters) == 0
#         assert doujin.chapters_count == 0
#         assert doujin.id == 'manga-kb951984'
#         assert doujin.title.english == "Monster Musume No Iru Nichijou"
#         assert doujin.title.japanese == "モンスター娘のいる日常"
#         assert doujin.title.other == "魔物娘的同居日常"
#         for genre in doujin.genres:
#             assert isinstance(genre, Genre)
        
#         for author in doujin.authors:
#             assert isinstance(author, Author)

#         assert isinstance(doujin.thumbnail, Image)
#         assert isinstance(doujin.cover, Image)
    
#     def test_get_with_symbolic_link(self):

#             doujin = self.sut.get(identifier='manga-kb951984', with_symbolic_links=True)

#             assert doujin is not None
#             assert isinstance(doujin.chapters[0], Chapter)
#             assert doujin.chapters[0].link is not None
#             assert doujin.chapters[0].link != ""

# class TestMangadexSourcePaginationMethod:
#     sut = Mangadex()

#     def test_success_searching(self):
#         res = self.sut.paginate(page=2)

#         assert res is not None
#         assert res.id == 0
#         assert res.page == 2
#         assert res.total_pages > 0
#         assert res.total_results > 0
#         assert len(res.results) == 24
        
#     @patch('requests.get')
#     def test_must_return_empty_search_result(self, mock_method: MagicMock):
#         mock = Mock()
#         mock.status_code = 200

#         mock.text = Mangadex_manga_page_empty_pagination_mocked

#         mock_method.return_value = mock
        
#         res = self.sut.paginate(page=2)

#         assert res is not None
#         assert res.id == 0
#         assert res.page == 2
#         assert res.total_pages > 0
#         assert res.total_results > 0
#         assert len(res.results) == 0

#     @patch('requests.get')
#     def test_response_when_forbidden(self, mock_method: MagicMock):
#         mock = Mock()
#         mock.status_code = 403
#         mock_method.return_value = mock
        
#         res = self.sut.paginate(page=2)
        
#         assert res is not None
#         assert res.id == 0
#         assert res.page == 2
#         assert res.total_pages == 1
#         assert res.total_results == 0
#         assert len(res.results) == 0

class TestMangadexSourceSearchMethod:

    sut = Mangadex()

    def test_success_searching(self):

        res = self.sut.search(query='GATE', page=1)

        assert res is not None
        assert res.query == 'GATE'
        assert res.id == 0
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
        assert res.id == 0
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

    