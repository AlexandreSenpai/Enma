import copy
from unittest.mock import MagicMock, Mock, patch
import sys
import os

import pytest


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.infra.core.interfaces.nhentai_response import NHentaiImage
from enma.application.core.handlers.error import InvalidConfig, InvalidRequest, NhentaiSourceWithoutConfig
from enma.domain.entities.pagination import Thumb
from tests.data.mocked_doujins import (nhentai_doujin_mocked, 
                                       nhentai_search_mocked, 
                                       nhentai_search_no_result_mocked, 
                                       nhentai_paginate_mocked, 
                                       nhentai_author_mocked,
                                       nhentai_author_not_found_mocked)
from enma.infra.adapters.repositories.nhentai import CloudFlareConfig, NHentai, Sort
from enma.domain.entities.manga import MIME, Author, Chapter, Genre, Image, Manga, SymbolicLink
from enma.application.core.utils.logger import logger

class TestNHentaiUtils:
    sut = NHentai(config=CloudFlareConfig(user_agent='mock', cf_clearance='mock'))

    @patch.object(logger, 'error')
    def test_request_error_handler(self, logger_mock: MagicMock):
        res = self.sut._NHentai__handle_request_error('teste') # type: ignore
        assert res is None
        logger_mock.assert_called_with('teste')
    
    def test_raise_error_if_passing_wrong_config(self):
        with pytest.raises(InvalidConfig) as err:
            self.sut.set_config(config={}) # type: ignore
    
    def test_set_config_successfully(self):
        res = self.sut.set_config(config=CloudFlareConfig(user_agent='mocked', cf_clearance='mocked'))
        assert res is None

    def test_set_config_must_raise_in_case_of_empty_values(self):
        with pytest.raises(InvalidRequest):
            self.sut.set_config(config=CloudFlareConfig(user_agent='', cf_clearance=''))

    def test_request_maker_must_raise_an_error_if_called_without_config(self):
        self.sut._NHentai__config = None # type: ignore
        with pytest.raises(NhentaiSourceWithoutConfig):
            self.sut._NHentai__make_request(url='https://www.google.com') # type: ignore

    @patch('requests.get')
    def test_make_a_request_successfully(self, request_mock: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = {}
        request_mock.return_value = mock

        self.sut.set_config(config=CloudFlareConfig(user_agent='mocked', cf_clearance='mocked'))
        res = self.sut._NHentai__make_request(url='https://www.google.com', headers={'add': 'header'}, params={'new': 'parameter'}) # type: ignore

        assert res.status_code == 200
        assert res.json() == {}

        request_mock.assert_called_once_with(url='https://www.google.com', 
                                             headers={'User-Agent': 'mocked', 
                                                      'add': 'header'},
                                             params={'new': 'parameter'},
                                             cookies={'cf_clearance': 'mocked'})

    def test_making_page_uri(self):
        page = self.sut._NHentai__make_page_uri(type='page', media_id='1234', mime=MIME.J, page_number=1) # type: ignore
        assert page == 'https://i.nhentai.net/galleries/1234/1.jpg'

    def test_making_cover_uri(self):
        page = self.sut._NHentai__make_page_uri(type='cover', media_id='1234', mime=MIME.J, page_number=1) # type: ignore
        assert page == 'https://t.nhentai.net/galleries/1234/cover.jpg'

    def test_making_thumbnail_uri(self):
        page = self.sut._NHentai__make_page_uri(type='thumbnail', media_id='1234', mime=MIME.J, page_number=1) # type: ignore
        assert page == 'https://t.nhentai.net/galleries/1234/thumb.jpg'

    def test_chapter_creator(self):
        images: list[NHentaiImage] = [{
            'h': 123,
            'w': 123,
            't': 'j'
        }]
        chapter = self.sut._NHentai__create_chapter(url='https://nhentai.net/g/1234', with_symbolic_links=False, media_id='12', pages=images) # type: ignore
        assert isinstance(chapter, Chapter)
        assert len(chapter.pages) == 1
        assert chapter.pages_count == 1
        assert isinstance(chapter.pages[0], Image)
        assert chapter.pages[0].width == 123
        assert chapter.pages[0].height == 123
        assert chapter.pages[0].mime.name == 'J'
        assert chapter.link is None

    def test_chapter_creator_with_symbolic_links(self):
        images: list[NHentaiImage] = [{
            'h': 123,
            'w': 123,
            't': 'j'
        }]
        chapter = self.sut._NHentai__create_chapter(url='https://nhentai.net/g/1234', with_symbolic_links=True, media_id='12', pages=images) # type: ignore
        assert isinstance(chapter, Chapter)
        assert len(chapter.pages) == 0
        assert chapter.pages_count == 0
        assert chapter.link == SymbolicLink(link='https://nhentai.net/g/1234')

class TestNHentaiSourceGetMethod:

    sut = NHentai(config=CloudFlareConfig(user_agent='mock', cf_clearance='mock'))

    @patch('requests.get')
    def test_success_doujin_retrieve(self, sut_mock: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = nhentai_doujin_mocked

        sut_mock.return_value = mock

        res = self.sut.get(identifier='1')

        assert res is not None
        assert res.id == 1
        assert res.title.english == "(C71) [Arisan-Antenna (Koari)] Eat The Rich! (Sukatto Golf Pangya)"
        assert res.title.japanese == "(C71) [ありさんアンテナ (小蟻)] Eat The Rich! (スカッとゴルフ パンヤ)"
        assert res.title.other == "Eat The Rich!"
        
        for genre in res.genres:
            assert isinstance(genre, Genre)
        
        for author in res.authors:
            assert isinstance(author, Author)

        assert isinstance(res.thumbnail, Image)
        assert isinstance(res.cover, Image)

        for chapter in res.chapters:
            assert isinstance(chapter, Chapter)

    @patch('requests.get')
    def test_must_return_other_titles_as_none_if_doesnt_exists(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200

        data = copy.deepcopy(nhentai_doujin_mocked)    
        data['title']['japanese'] = None # type: ignore
        data['title']['pretty'] = None # type: ignore

        mock.json.return_value = data
        
        mock_method.return_value = mock
        
        manga = self.sut.get(identifier='489504')

        assert manga is not None
        assert manga.id == 1
        assert manga.title.english == "(C71) [Arisan-Antenna (Koari)] Eat The Rich! (Sukatto Golf Pangya)"
        assert manga.title.japanese == None
        assert manga.title.other == None

    @patch('requests.get')
    def test_response_when_it_could_not_get_doujin(self, mock_method: MagicMock):
        mock_method.status_code = 404

        doujin = self.sut.get(identifier='1')
        
        assert doujin is None
    
    @patch('requests.get')
    def test_return_none_when_not_receive_200_status_code(self, mock_method: MagicMock):
            mock = Mock()
            mock.status_code = 403
            mock_method.return_value = mock

            doujin = self.sut.get(identifier='1')

            assert doujin is None
            mock_method.assert_called_with(url=f'https://nhentai.net/api//gallery/1',
                                           headers={'User-Agent': 'mock'},
                                           params={},
                                           cookies={'cf_clearance': 'mock'})
    
    @patch('requests.get')
    def test_return_empty_chapters(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200
        
        data = copy.deepcopy(nhentai_doujin_mocked) 
        data['images']['pages'] = []
        mock.json.return_value = data

        mock_method.return_value = mock

        doujin = self.sut.get(identifier='1')

        assert doujin is not None
        assert isinstance(doujin.chapters[0], Chapter)
        assert len(doujin.chapters[0].pages) == 0
        assert doujin.id == 1 

    @patch('requests.get')
    def test_return_right_mime(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200

        mock.json.return_value = nhentai_doujin_mocked

        mock_method.return_value = mock

        doujin = self.sut.get(identifier='1')

        assert doujin is not None
        assert isinstance(doujin.chapters[0], Chapter)
        assert doujin.chapters[0].pages[0].mime.value == 'jpg'
        assert nhentai_doujin_mocked['images']['pages'][0]['t'] == 'j'
        assert doujin.cover is not None
        assert doujin.cover.mime.value == 'png'
        assert nhentai_doujin_mocked['images']['cover']['t'] == 'p'
        assert doujin.chapters[0].link is None
    
    @patch('requests.get')
    def test_get_with_symbolic_link(self, mock_method: MagicMock):
            mock = Mock()
            mock.status_code = 200

            mock.json.return_value = nhentai_doujin_mocked

            mock_method.return_value = mock

            doujin = self.sut.get(identifier='420719', with_symbolic_links=True)

            assert doujin is not None
            assert isinstance(doujin.chapters[0], Chapter)
            assert doujin.chapters[0].link is not None
            assert doujin.chapters[0].link != ""

    @patch('requests.get')
    def test_language_must_be_present(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = nhentai_doujin_mocked

        mock_method.return_value = mock

        doujin = self.sut.get(identifier='420719', with_symbolic_links=True)

        assert doujin is not None
        assert doujin.language is not None
        assert doujin.language == 'japanese'

    @patch('requests.get')
    def test_images_mime_types_must_be_correct(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = nhentai_doujin_mocked

        mock_method.return_value = mock

        doujin = self.sut.get(identifier='420719', with_symbolic_links=True)

        assert doujin is not None
        assert doujin.cover is not None        
        assert doujin.thumbnail is not None

        cover_mime = nhentai_doujin_mocked['images']['cover']['t']
        thumb_mime = nhentai_doujin_mocked['images']['thumbnail']['t']

        assert cover_mime.upper() == doujin.cover.mime.name
        assert thumb_mime.upper() == doujin.thumbnail.mime.name

class TestNHentaiSourcePaginationMethod:
    sut = NHentai(config=CloudFlareConfig(user_agent='mock', cf_clearance='mock'))

    @patch('requests.get')
    def test_success_searching(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = nhentai_paginate_mocked

        mock_method.return_value = mock

        res = self.sut.paginate(page=2)

        assert res is not None
        assert res.id == 0
        assert res.page == 2
        assert res.total_pages == nhentai_paginate_mocked['num_pages']
        assert res.total_results == 25 * 19163
        assert len(res.results) == nhentai_paginate_mocked['per_page']
        
    @patch('requests.get')
    def test_must_return_empty_search_result(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200

        copied = copy.deepcopy(nhentai_paginate_mocked)
        copied['result'] = [] # type: ignore        
        mock.json.return_value = copied

        mock_method.return_value = mock
        
        res = self.sut.paginate(page=2)

        assert res is not None
        assert res.id == 0
        assert res.page == 2
        assert res.total_pages == nhentai_paginate_mocked['num_pages']
        assert res.total_results == 25 * 19163
        assert len(res.results) == 0

    def test_response_when_forbidden(self):
        res = self.sut.paginate(page=2)
        
        assert res is not None
        assert res.id == 0
        assert res.page == 2
        assert res.total_pages == 1
        assert res.total_results == 0
        assert len(res.results) == 0

class TestNHentaiSourceSearchMethod:

    sut = NHentai(config=CloudFlareConfig(user_agent='mock', cf_clearance='mock'))

    @patch('requests.get')
    def test_success_searching(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.text = nhentai_search_mocked

        mock_method.return_value = mock

        res = self.sut.search(query='GATE', page=2)

        assert res is not None
        assert res.query == 'GATE'
        assert res.id == 0
        assert res.page == 2
        assert res.total_pages == 3
        assert len(res.results) == 25

        for result in res.results:
            assert isinstance(result, Thumb)
            assert result.cover is not None
            assert isinstance(result.cover, Image)
            assert isinstance(result.cover.width, int)
            assert isinstance(result.cover.height, int)
            assert result.cover.width > 0
            assert result.cover.height > 0
            assert result.title is not None
            assert result.id != 0

        mock_method.assert_called_once_with(url='https://nhentai.net/search',
                                            params={'q': 'GATE',
                                                    'sort': Sort.RECENT.value,
                                                    'page': 2},
                                            headers={'User-Agent': 'mock'},
                                            cookies={'cf_clearance': 'mock'})
        
    @patch('requests.get')
    def test_must_return_empty_search_result(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.text = nhentai_search_no_result_mocked
        mock_method.return_value = mock
        
        res = self.sut.search(query='GATE', page=2)

        assert res is not None
        assert res.query == 'GATE'
        assert res.id == 0
        assert res.page == 2
        assert res.total_pages == 1
        assert len(res.results) == 0

    def test_response_when_forbidden(self):
        search = self.sut.search(query='Monster Musume no Iru Nichijou', page=4)
        
        assert search is not None
        assert search is not None
        assert search.query == 'Monster Musume no Iru Nichijou'
        assert search.id == 0
        assert search.page == 4
        assert search.total_pages == 1
        assert len(search.results) == 0

class TestNHentaiSourceAuthorPageMethod:

    sut = NHentai(config=CloudFlareConfig(user_agent='mock', cf_clearance='mock'))

    @patch('requests.get')
    def test_success_author_page_fetching(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.text = nhentai_author_mocked

        mock_method.return_value = mock

        res = self.sut.author_page(author='akaneman', page=2)

        assert res is not None
        assert res.author == 'akaneman'
        assert res.id == 0
        assert res.page == 2
        assert res.total_pages == 2
        assert len(res.results) == 25

        for result in res.results:
            assert isinstance(result, Thumb)
            assert result.cover is not None
            assert isinstance(result.cover, Image)
            assert isinstance(result.cover.width, int)
            assert isinstance(result.cover.height, int)
            assert result.cover.width > 0
            assert result.cover.height > 0
            assert result.title is not None
            assert result.id != 0

        mock_method.assert_called_once_with(url='https://nhentai.net/artist/akaneman',
                                            params={'page': 2},
                                            headers={'User-Agent': 'mock'},
                                            cookies={'cf_clearance': 'mock'})
        
    @patch('requests.get')
    def test_must_return_empty_author_page_result(self, mock_method: MagicMock):
        mock = Mock()
        mock.status_code = 200
        mock.text = nhentai_author_not_found_mocked
        mock_method.return_value = mock
        
        res = self.sut.author_page(author='asdsadadasd', page=1)

        assert res is not None
        assert res.author == 'asdsadadasd'
        assert res.id == 0
        assert res.page == 1
        assert res.total_pages == 1
        assert len(res.results) == 0

    def test_response_when_forbidden(self):
        search = self.sut.author_page(author='akaneman', page=1)
        
        assert search is not None
        assert search is not None
        assert search.author == 'akaneman'
        assert search.id == 0
        assert search.page == 1
        assert search.total_pages == 1
        assert len(search.results) == 0
