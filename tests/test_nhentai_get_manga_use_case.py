import datetime
import json
from unittest.mock import MagicMock, Mock, patch
import sys
import os

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.application.core.handlers.error import Forbidden, NotFound
from enma.infra.core.interfaces.nhentai_response import NHentaiResponse
from enma.application.use_cases.get_manga import GetMangaRequestDTO, GetMangaUseCase
from enma.application.core.interfaces.use_case import DTO
from enma.infra.adapters.repositories.nhentai import CloudFlareConfig, NHentai
from enma.domain.entities.manga import MIME, Author, Chapter, Genre, Image, Manga, Title

class TestNHentaiGetDoujin:

    nhentai = NHentai(config=CloudFlareConfig(user_agent='mocked',
                                              cf_clearance='mocked'))
    sut = GetMangaUseCase(manga_repository=nhentai)

    mocked_manga = Manga(title=Title(english="[Hikoushiki (CowBow)] Marine Senchou no Yopparai Archive | Marine's Drunken Archives (Houshou Marine) [English] [Watson] [Digital]",
                                     japanese='[飛行式 (矼房)] マリン船長の酔っぱっぱアーカイブ (宝鐘マリン) [英訳] [DL版]',
                                     other="Marine Senchou no Yopparai Archive | Marine's Drunken Archives"),
                         status='completed',
                         url='mocked',
                         id=489504,
                         created_at=datetime.datetime(2024, 1, 7, 0, 3, 25, tzinfo=datetime.timezone.utc),
                         updated_at=datetime.datetime(2024, 1, 7, 0, 3, 25, tzinfo=datetime.timezone.utc),
                         authors=[Author(name='cowbow')],
                         genres=[Genre(name='sweating', id=1590)],
                         thumbnail=Image(uri='https://i.nhentai.net/galleries/2786266/22.jpg', name='21.jpg', width=1280, height=1808, mime=MIME.J),
                         cover=Image(uri='https://i.nhentai.net/galleries/2786266/22.jpg', name='21.jpg', width=1280, height=1808, mime=MIME.J),
                         chapters=[Chapter(id=0, pages=[Image(uri='https://i.nhentai.net/galleries/2786266/1.jpg', name='0.jpg', width=1280, height=1807, mime=MIME.J),
                                                        Image(uri='https://i.nhentai.net/galleries/2786266/2.jpg', name='1.jpg', width=1280, height=1807, mime=MIME.J)])])

    def test_success_doujin_retrieve(self):
        with patch('enma.infra.adapters.repositories.nhentai.NHentai.get') as mock_method:
            mock_method.return_value = self.mocked_manga
            res = self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='489504')))

            assert res.found == True
            assert res.manga is not None
            assert res.manga.id == 489504
            assert res.manga.title.english == "[Hikoushiki (CowBow)] Marine Senchou no Yopparai Archive | Marine's Drunken Archives (Houshou Marine) [English] [Watson] [Digital]"
            assert res.manga.title.japanese == "[飛行式 (矼房)] マリン船長の酔っぱっぱアーカイブ (宝鐘マリン) [英訳] [DL版]"
            assert res.manga.title.other == "Marine Senchou no Yopparai Archive | Marine's Drunken Archives"
            
            for genre in res.manga.genres:
                assert isinstance(genre, Genre)
            
            for author in res.manga.authors:
                assert isinstance(author, Author)

            assert isinstance(res.manga.thumbnail, Image)
            assert isinstance(res.manga.cover, Image)

            for chapter in res.manga.chapters:
                assert isinstance(chapter, Chapter)
            
            mock_method.assert_called_with(identifier='489504', with_symbolic_links=False)

    def test_must_return_other_titles_as_none_if_doesnt_exists(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 200
            
            with open('./tests/data/get.json', 'r') as get:
                data: NHentaiResponse = json.loads(get.read())
                
                data['title']['japanese'] = None # type: ignore
                data['title']['pretty'] = None # type: ignore

                mock.json.return_value = data
            
            mock_method.return_value = mock
            
            res = self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='489504')))

            assert res.found == True
            assert res.manga is not None
            assert res.manga.id == 1
            assert res.manga.title.english == "(C71) [Arisan-Antenna (Koari)] Eat The Rich! (Sukatto Golf Pangya)"
            assert res.manga.title.japanese == None
            assert res.manga.title.other == None
        
    def test_response_when_it_could_not_get_doujin(self):
        with patch('enma.infra.adapters.repositories.nhentai.NHentai.get', side_effect=NotFound("Could not find the manga")) as mock_method:
            doujin = self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='1')))
            assert doujin.found == False
            assert doujin.manga is None
    
    def test_raise_forbidden_in_case_of_403(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 403
            mock_method.return_value = mock

            with pytest.raises(Forbidden):
                self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='1')))
                mock_method.assert_called_with(url=f'https://nhentai.net/api//gallery/1',
                                            headers={'User-Agent': 'mocked'},
                                            params={},
                                            cookies={'cf_clearance': 'mocked'})

    def test_return_empty_chapters(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 200

            with open('./tests/data/get.json', 'r') as get:
                data = json.loads(get.read())
                data['images']['pages'] = []
                mock.json.return_value = data

            mock_method.return_value = mock

            doujin = self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='1')))

            assert doujin.found == True
            assert doujin.manga is not None
            assert isinstance(doujin.manga.chapters[0], Chapter)
            assert len(doujin.manga.chapters[0].pages) == 0
            assert doujin.manga.id == 1 

    def test_return_right_mime(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 200

            with open('./tests/data/get.json', 'r') as get:
                data = json.loads(get.read())
                mock.json.return_value = data

            mock_method.return_value = mock

            doujin = self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='2')))

            assert doujin.found == True
            assert doujin.manga is not None
            assert isinstance(doujin.manga.chapters[0], Chapter)
            assert doujin.manga.chapters[0].pages[0].mime.value == 'jpg'
            assert data['images']['pages'][0]['t'] == 'j'
            assert doujin.manga.cover is not None
            assert doujin.manga.cover.mime.value == 'png'
            assert data['images']['cover']['t'] == 'p'
            assert doujin.manga.chapters[0].link is None

    def test_get_with_symbolic_link(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 200

            with open('./tests/data/get.json', 'r') as get:
                data = json.loads(get.read())
                mock.json.return_value = data

            mock_method.return_value = mock

            doujin = self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='420719', with_symbolic_links=True)))

            assert doujin.found == True
            assert doujin.manga is not None
            assert isinstance(doujin.manga.chapters[0], Chapter)
            assert doujin.manga.chapters[0].link is not None
            assert doujin.manga.chapters[0].link != ""

    def test_language_must_be_present(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 200

            with open('./tests/data/get.json', 'r') as get:
                data = json.loads(get.read())
                mock.json.return_value = data

            mock_method.return_value = mock

            doujin = self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='420719', with_symbolic_links=True)))

            assert doujin.found == True
            assert doujin.manga is not None
            assert doujin.manga.language is not None
            assert doujin.manga.language == 'japanese'

    def test_images_mime_types_must_be_correct(self):
        with patch('requests.get') as mock_method:
            mock = Mock()
            mock.status_code = 200
            
            with open('./tests/data/get.json', 'r') as get:
                data: NHentaiResponse = json.loads(get.read())
                mock.json.return_value = data

            mock_method.return_value = mock

            doujin = self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='420719', with_symbolic_links=True)))

            assert doujin.found == True
            assert doujin.manga is not None
            
            cover_mime = data['images']['cover']['t']
            thumb_mime = data['images']['thumbnail']['t']

            assert doujin.manga.thumbnail is not None
            assert doujin.manga.cover is not None
            assert cover_mime.upper() == 'P'
            assert doujin.manga.cover.mime.value == 'png'
            assert thumb_mime.upper() == 'J'
            assert doujin.manga.thumbnail.mime.value == 'jpg'

    @patch('enma.application.use_cases.get_manga.GetMangaUseCase.execute')
    def test_symbolic_links_must_be_disabled_by_default(self, use_case_mock: MagicMock):
        self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='420719')))
        use_case_mock.assert_called_with(dto=DTO(data=GetMangaRequestDTO(identifier='420719', with_symbolic_links=False)))

    def test_must_raise_an_exception_case_user_has_provided_wrong_data_type(self):
        with pytest.raises(ValidationError) as _:
            self.sut.execute(dto=DTO(data=GetMangaRequestDTO(identifier='420719', with_symbolic_links='nao'))) # type: ignore
