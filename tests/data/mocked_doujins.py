import json

from enma.infra.core.interfaces.mangadex_response import ISearchResult
from enma.infra.core.interfaces.nhentai_response import NHentaiPaginateResponse, NHentaiResponse

with open('./tests/data/get.json', 'r') as get:
    nhentai_doujin_mocked: NHentaiResponse = json.loads(get.read())

with open('./tests/data/nhentai_search_mock.txt', 'r') as search:
    nhentai_search_mocked = search.read()

with open('./tests/data/nhentai_search_no_result.txt', 'r') as no_result:
    nhentai_search_no_result_mocked = no_result.read()

with open('./tests/data/nhentai_paginate_mock.json', 'r') as paginate:
    nhentai_paginate_mocked: NHentaiPaginateResponse = json.loads(paginate.read())

with open('./tests/data/nhentai_author_page_mock.txt', 'r') as author:
    nhentai_author_mocked = author.read()

with open('./tests/data/nhentai_author_page_not_found_mock.txt', 'r') as author_not_found:
    nhentai_author_not_found_mocked = author_not_found.read()

with open('./tests/data/manganato_manga_page_empty_chapters_mock.txt', 'r') as empty_ch:
    manganato_manga_page_empty_chapters_mocked = empty_ch.read()

with open('./tests/data/manganato_manga_page_empty_pagination_mock.txt', 'r') as empty_pag:
    manganato_manga_page_empty_pagination_mocked = empty_pag.read()

with open('./tests/data/mangadex_empty_pagination_mock.json', 'r') as paginate:
    mangadex_paginate_mocked: ISearchResult = json.loads(paginate.read())
