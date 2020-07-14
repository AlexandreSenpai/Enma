from NHentai import NHentai

def test_case01():
    doujin = NHentai().get_doujin('320165')
    assert doujin is not None

def test_case02():
    doujin = NHentai().get_doujin('320066')
    assert doujin is not None

def test_case03():
    doujin = NHentai().get_doujin('320067')
    assert doujin is not None

def test_case04():
    doujin = NHentai().get_doujin('0656654654')
    assert doujin is None

def test_case05():
    doujin = NHentai().get_doujin('1212145487')
    assert doujin is None

def test_case06():
    doujin = NHentai().get_doujin('320290')
    assert doujin is not None

def test_case07():
    doujin = NHentai().get_doujin('full color')
    assert doujin is None
