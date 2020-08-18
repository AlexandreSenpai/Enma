import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from nhentai import NHentai

def test_case01():
    doujin = NHentai().get_random()
    assert doujin.get('id') is not None
    assert doujin.get('title') is not None
    assert doujin.get('secondary_title') is not None
    assert doujin.get('tags') is not None
    assert doujin.get('artists') is not None
    assert doujin.get('languages') is not None
    assert doujin.get('categories') is not None
    assert doujin.get('pages') is not None
    assert doujin.get('images') is not None

def test_case02():
    doujin = NHentai().get_random()
    assert doujin is not None

def test_case03():
    doujin = NHentai().get_random()
    assert doujin is not None

def test_case04():
    doujin = NHentai().get_random()
    assert doujin is not None

def test_case05():
    doujin = NHentai().get_random()
    assert doujin is not None

def test_case06():
    doujin = NHentai().get_random()
    assert doujin is not None

def test_case07():
    doujin = NHentai().get_random()
    assert doujin is not None
