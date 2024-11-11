import datetime
import json
from unittest.mock import Mock, patch
import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.application.core.handlers.error import NotFound
from enma.application.use_cases.fetch_chapter_by_symbolic_link import FetchChapterBySymbolicLinkRequestDTO, FetchChapterBySymbolicLinkUseCase
from enma.application.core.interfaces.use_case import DTO
from enma.infra.adapters.repositories.nhentai import CloudFlareConfig, NHentai
from enma.domain.entities.manga import MIME, Author, Chapter, Genre, Image, Manga, SymbolicLink, Title

class TestFetchChapterWithSymbolicLink:

    nhentai = NHentai(config=CloudFlareConfig(user_agent='mocked',
                                              cf_clearance='mocked'))
    sut = FetchChapterBySymbolicLinkUseCase(manga_repository=nhentai)

    mocked_manga = Manga(title=Title(english="[Hikoushiki (CowBow)] Marine Senchou no Yopparai Archive | Marine's Drunken Archives (Houshou Marine) [English] [Watson] [Digital]",
                                     japanese='[飛行式 (矼房)] マリン船長の酔っぱっぱアーカイブ (宝鐘マリン) [英訳] [DL版]',
                                     other="Marine Senchou no Yopparai Archive | Marine's Drunken Archives"),
                         status='completed',
                         url="mocked",
                         id=489504,
                         created_at=datetime.datetime(2024, 1, 7, 0, 3, 25, tzinfo=datetime.timezone.utc),
                         updated_at=datetime.datetime(2024, 1, 7, 0, 3, 25, tzinfo=datetime.timezone.utc),
                         authors=[Author(name='cowbow')],
                         genres=[Genre(name='sweating', id=1590)],
                         thumbnail=Image(uri='https://i.nhentai.net/galleries/2786266/22.jpg', name='21.jpg', width=1280, height=1808, mime=MIME.J),
                         cover=Image(uri='https://i.nhentai.net/galleries/2786266/22.jpg', name='21.jpg', width=1280, height=1808, mime=MIME.J),
                         chapters=[Chapter(id=0, pages=[Image(uri='https://i.nhentai.net/galleries/2786266/1.jpg', name='0.jpg', width=1280, height=1807, mime=MIME.J),
                                                        Image(uri='https://i.nhentai.net/galleries/2786266/2.jpg', name='1.jpg', width=1280, height=1807, mime=MIME.J)])])

    def test_fetch_chapter_by_symbolic_link(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 200
            
            with open('./tests/data/get.json', 'r') as get:
                data = json.loads(get.read())
                mock.json.return_value = data

            mock_method.return_value = mock

            link = SymbolicLink(link='https://nhentai.net/api/gallery/1')
            response = self.sut.execute(dto=DTO(data=FetchChapterBySymbolicLinkRequestDTO(link=link)))

            assert isinstance(response.chapter, Chapter)
            assert response.chapter.pages_count == 14
            assert response.chapter.id == 0
            assert len(response.chapter.pages) == 14

    def test_should_raise_exception_for_broken_link(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 404
            mock.json.return_value = {}
            mock_method.return_value = mock

            link = SymbolicLink(link='https://nhentai.net')
            
            with pytest.raises(NotFound):
                self.sut.execute(dto=DTO(data=FetchChapterBySymbolicLinkRequestDTO(link=link)))
        
    def test_should_return_empty_chapter_for_broken_response(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 200
            mock.json.return_value = {}
            mock_method.return_value = mock

            link = SymbolicLink(link='https://nhentai.net')
            response = self.sut.execute(dto=DTO(data=FetchChapterBySymbolicLinkRequestDTO(link=link)))
            
            assert isinstance(response.chapter, Chapter)
            assert response.chapter.link is None
            assert response.chapter.pages_count == 0
            assert response.chapter.id == 0
            assert len(response.chapter.pages) == 0
