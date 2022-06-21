from urllib.parse import urljoin

from bs4 import BeautifulSoup

from NHentai.core.logging import logger
from NHentai.core.interfaces import Comment, CommentPage, Doujin, SearchResult, Sort, PopularPage, Page
from NHentai.sync.infra.adapters.repositories.hentai.hentai_interface import NhentaiInterface
from NHentai.sync.infra.adapters.request.http.implementations.sync import RequestsAdapter


class NHentaiAdapter(NhentaiInterface):

    _BASE_URL = 'https://nhentai.net/'
    _API_URL = 'https://nhentai.net/api/'
    _IMAGE_BASE_URL = 'https://i.nhentai.net/galleries/'
    _AVATAR_URL = 'https://i5.nhentai.net/'
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
            logger.warn('Could not find any search results.')
            return SearchResult(query=search_term,
                                sort=sort if isinstance(sort, str) else sort.value,
                                total_pages=total_pages,
                                page=page,
                                total_results=0,
                                doujins=[])
        
        a_tags_with_doujin_id = [gallery.find('a', {'class': 'cover'}) for gallery in search_results]

        doujin_ids = [[]]
        doujins = []
        doujin_per_async_request = 2
        for a_tag in a_tags_with_doujin_id:
            if a_tag is None:
                continue

            doujin_id = a_tag['href'].split('/')[-2]
            if doujin_id != '':
                last_doujin_id_list = doujin_ids[-1]
                if len(last_doujin_id_list) < doujin_per_async_request: doujin_ids[-1].append(int(doujin_id))
                else: doujin_ids.append([int(doujin_id)])
        
        for chunk_ids in doujin_ids:
            doujins.extend([self.get_doujin(doujin_id) for doujin_id in chunk_ids])

        return SearchResult(query=search_term,
                            sort=sort if isinstance(sort, str) else sort.value,
                            total_pages=total_pages,
                            page=page,
                            total_results=25*total_pages if pagination_container else len(doujin_ids),
                            doujins=doujins)
        
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

    def get_comments(self, doujin_id: int) -> CommentPage:
        """This method returns all comments of a doujin.
        Args:
            doujin_id:
                Id of the doujin.
        Returns:

        """
        
        request_response = self.request_adapter.get(urljoin(self._API_URL, f'gallery/{doujin_id}/comments'))
        
        comments = [Comment.from_json(json_object=comment_json, avatar_url=self._AVATAR_URL) for comment_json in request_response.json()]
        
        return CommentPage(comments=comments,
                           total_comments=len(comments))
        
    def get_page(self, page: int=1) -> Page:
        """This method paginates through the homepage of NHentai and returns the doujins.
        Args:
            page: number of the pagination page.
        Returns:
            HomePage: dataclass with a list of Doujin.
                You can access the dataclass information in the `entities` folder.
        """

        logger.info(f'Fetching page {page} of homepage')
        request_response = self.request_adapter.get(urljoin(self._API_URL, f'galleries/all'),
                                                          params={'page': page})
        data = request_response.json()
        

        DOUJINS = [Doujin.from_json(json_obj,
                                    self._BASE_URL,
                                    self._IMAGE_BASE_URL,
                                    self._TINY_IMAGE_BASE_URL) for json_obj in data.get('result')]

        PAGES = data.get('num_pages', 0)
        PER_PAGE = data.get('per_page', 0)
        TOTAL_RESULTS = int(PAGES) * int(PER_PAGE)

        return Page(
            doujins=DOUJINS,
            total_results=TOTAL_RESULTS,
            total_pages=PAGES,
            per_page=PER_PAGE,
            page=int(page))