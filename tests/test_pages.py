from NHentai import NHentai

def test_evoke():
    pages = NHentai().get_pages()

    doujins = pages.get('doujins', [])

    for doujin in doujins:
        print(doujin.get('lang'), sep=' ')

test_evoke()