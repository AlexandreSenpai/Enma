import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.infra.adapters.repositories.mangadex import Mangadex
from enma.infra.entrypoints.lib import SourceManager, Sources
from enma.application.core.handlers.error import InstanceError, SourceNotAvailable

class TestSourceManager:

    sut = SourceManager()

    @pytest.fixture(autouse=True)
    def run_around_tests(self):
        yield
        self.sut.clear_sources()

    def test_add_source_successfully(self):
        self.sut.add_source(source_name=Sources.MANGADEX, source=Mangadex())
        assert self.sut.get_source(Sources.MANGADEX) is not None

    def test_get_source_should_raise_exception_if_source_doesnt_exists(self):
        with pytest.raises(SourceNotAvailable):
            self.sut.get_source(Sources.NHENTAI)

    def test_get_source_successfully_with_string_parameter(self):
        self.sut.add_source(source_name=Sources.MANGADEX, source=Mangadex())
        assert isinstance(self.sut.get_source('mangadex'), IMangaRepository)

    def test_clear_sources_successfully(self):
        self.sut.add_source(source_name=Sources.MANGADEX, source=Mangadex())
        self.sut.clear_sources()
        with pytest.raises(SourceNotAvailable):
            self.sut.get_source(Sources.MANGADEX)

    def test_remove_source_successfully(self):
        self.sut.add_source(source_name=Sources.MANGADEX, source=Mangadex())
        assert self.sut.remove_source(Sources.MANGADEX) is True
        with pytest.raises(SourceNotAvailable):
            self.sut.get_source(Sources.MANGADEX)

    def test_remove_source_should_return_false_if_source_doesnt_exists(self):
        assert self.sut.remove_source(Sources.MANGADEX) is False

    def test_set_source_successfully(self):
        self.sut.add_source(source_name=Sources.MANGADEX, source=Mangadex())
        self.sut.set_source(Sources.MANGADEX)
        assert self.sut.source is not None

    def test_should_not_be_able_to_add_an_source_that_is_not_imanga_repository(self):
        with pytest.raises(InstanceError):
            self.sut.add_source(source_name=Sources.MANGADEX, source=object()) # type: ignore
