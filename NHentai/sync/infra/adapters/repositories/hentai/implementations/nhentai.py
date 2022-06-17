import asyncio
import random
import time
from urllib.parse import urljoin

from NHentai.sync.infra.utils import ThreadWithReturnValue
from NHentai.core.logging import logger
from NHentai.sync.infra.adapters.repositories.hentai.hentai_interface import NhentaiInterface
from NHentai.sync.infra.adapters.repositories.hentai.interfaces import Doujin, SearchResult, Sort, PopularPage

from NHentai.sync.infra.adapters.request.http.implementations.sync import RequestsAdapter


from bs4 import BeautifulSoup

class NHentaiAdapter(NhentaiInterface):

    _BASE_URL = 'https://nhentai.net/'
    _API_URL = 'https://nhentai.net/api/'
    _IMAGE_BASE_URL = 'https://i.nhentai.net/galleries/'
    _TINY_IMAGE_BASE_URL = _IMAGE_BASE_URL.replace('/i.', '/t.')


    def __init__(self, request_adapter: RequestsAdapter):
        self.request_adapter = request_adapter
        self.scrapper_adapter = BeautifulSoup

    def get_doujin(self, doujin_id: int) -> Doujin:
        """This method fetches a doujin information based on id.
        Args:
            id: 
                Id of the target doujin.
        Returns:
            Doujin: 
                dataclass with the doujin information within.
        """

        logger.info(f'Retrieving doujin with id {doujin_id}')

        request_response = self.request_adapter.get(urljoin(self._API_URL, f'gallery/{doujin_id}'))

        logger.info(f'Sucessfully retrieved doujin {doujin_id}')

        return Doujin.from_json(json_object=request_response.json(), 
                                base_url=self._BASE_URL,
                                image_base_url_prefix=self._IMAGE_BASE_URL,
                                tiny_image_base_url_prefix=self._TINY_IMAGE_BASE_URL)
    
    def search_doujin(self, search_term: str, page: int=1, sort: Sort=Sort.RECENT) -> SearchResult:
        request_response = self.request_adapter.get(urljoin(self._BASE_URL, 'search'), 
                                                    params={'q': search_term, 
                                                            'sort': sort if isinstance(sort, str) else sort.value, 
                                                            'page': page},
                                                    headers={'User-Agent': 'Mozilla/5.0'})

        soup = self.scrapper_adapter(request_response.text, 'html.parser')

        search_results_container = soup.find('div', {'class': 'container'})
        pagination_container = soup.find('section', {'class': 'pagination'})

        last_page_a_tag = pagination_container.find('a', {'class': 'last'}) if pagination_container else None
        total_pages = int(last_page_a_tag['href'].split('=')[-1]) if last_page_a_tag else 1
        
        if not search_results_container:
            logger.error('Could not find search result container.')
            return SearchResult(query=search_term,
                                sort=sort if isinstance(sort, str) else sort.value,
                                total_pages=total_pages,
                                page=page,
                                total_results=0,
                                doujins=[])
        
        search_results = search_results_container.find_all('div', {'class': 'gallery'})

        if not search_results:
            logger.error('Could not find any search results.')
            return SearchResult(query=search_term,
                                sort=sort if isinstance(sort, str) else sort.value,
                                total_pages=total_pages,
                                page=page,
                                total_results=0,
                                doujins=[])
        
        a_tags_with_doujin_id = [gallery.find('a', {'class': 'cover'}) for gallery in search_results]

        doujin_ids = list()
        for a_tag in a_tags_with_doujin_id:
            if a_tag is None:
                continue

            doujin_id = a_tag['href'].split('/')[-2]
            if doujin_id != '':
                doujin_ids.append(int(doujin_id))

        threads = [ThreadWithReturnValue(target=self.get_doujin, args=(doujin_id,)) for doujin_id in doujin_ids]
        
        for thread in threads:
            thread.start()
            time.sleep(random.uniform(0, 1))

        return SearchResult(query=search_term,
                            sort=sort if isinstance(sort, str) else sort.value,
                            total_pages=total_pages,
                            page=page,
                            total_results=25*total_pages if pagination_container else len(doujin_ids),
                            doujins=[thread.join() for thread in threads])
        
    def get_random(self) -> Doujin:
        request_response = self.request_adapter.get(urljoin(self._BASE_URL, 'random'))

        soup = self.scrapper_adapter(request_response.text, 'html.parser')

        id = soup.find('h3', id='gallery_id').text.replace('#', '')

        doujin = self.get_doujin(doujin_id=id)
            
        return doujin
    
    def get_popular_now(self) -> PopularPage:
        """This method retrieves a list of the current most popular doujins.
        Args:
        Returns:
            PopularPage: 
                dataclass with the current popular doujin list within.
            
            You can access the dataclasses informations at `entities` package.
        """

        request_response = self.request_adapter.get(self._BASE_URL)
        
        soup = self.scrapper_adapter(request_response.text, 'html.parser')
        
        popular_section = soup.find('div', class_='index-popular')
        DOUJINS = []

        for item in popular_section.find_all('div', class_='gallery'):
            DOUJIN_ID = item.find('a', class_='cover')['href'].split('/')[2]

            POPULAR_DOUJIN = self.get_doujin(DOUJIN_ID)

            if POPULAR_DOUJIN is not None:
                DOUJINS.append(POPULAR_DOUJIN)
        
        return PopularPage(doujins=DOUJINS,
                           total_doujins=len(DOUJINS))
