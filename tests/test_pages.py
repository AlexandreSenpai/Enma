import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from nhentai import NHentai

def test_payload_integrity():
    pages = NHentai().get_pages()

    doujins = pages.get('doujins', [])

    for doujin in doujins:
        assert doujin.get('id') != None 
        assert doujin.get('title') != None 
        assert doujin.get('lang') != None 
        assert doujin.get('cover') != None 
        assert doujin.get('data-tags') != None 

def test_user_payload_integrity():
    user = NHentai().get_user_page('3438840', 'kenzinho_boca_de_veludo')

    assert user.get('uid') != None 
    assert user.get('username') != None 
    assert user.get('since') != None 