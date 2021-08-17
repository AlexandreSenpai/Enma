import asyncio
import logging
import asyncio
from typing import AsyncGenerator
from urllib.parse import urljoin

from .utils.cache import Cache
from .base_wrapper import BaseWrapper
from .entities.doujin import Doujin, DoujinThumbnail
from .entities.page import (Page, 
                            SearchPage,
                            CharacterListPage,
                            PopularPage)
from .entities.links import CharacterLink 
from .entities.options import Sort


class NHentaiAsync(BaseWrapper):
    @Cache(max_age_seconds=3600, max_size=1000, cache_key_position=1, cache_key_name='id').async_cache
    async def get_doujin(self, id: str) -> Doujin:
        """This method fetches a doujin information based on id.

        Args:
            id: 
                Id of the target doujin.

        Returns:
            Doujin: 
                dataclass with the doujin information within.
            
            You can access the dataclasses informations at `entities` package.
        """

        print(f'INFO::Retrieving doujin with id {id}')
        id = str(id)

        if not id.isnumeric() or id[0] == '0':
            print('ERROR::Maybe you mistyped the doujin id or it doesnt exists.')
            return None

        SOUP = await self._async_fetch(urljoin(self._API_URL, f'gallery/{id}'), is_json=True)

        if SOUP.get('error'):
            print('ERROR::Maybe you mistyped the doujin id or it doesnt exists.')
            return None
         
        print(f'INFO::Sucessfully retrieved doujin {id}')

        return Doujin.from_json(SOUP)

    @Cache(max_age_seconds=3600, max_size=15, cache_key_position=1, cache_key_name='page').async_cache
    async def get_pages(self, page: int=1) -> Page:
        """This method paginates through the homepage of NHentai and returns the doujins.

        Args:
            page: 
                number of the pagination page.

        Returns:
            HomePage: 
                dataclass with a list of DoujinThumbnail.
            
            You can access the dataclasses informations at `entities` package.
        """

        print(f'INFO::Fetching page {page}')
        SOUP = await self._async_fetch(urljoin(self._API_URL, f'galleries/all?page={page}'), is_json=True)

        DOUJINS = [DoujinThumbnail.from_json(json_obj) for json_obj in SOUP.get('result')]
        PAGES = SOUP.get('num_pages')
        PER_PAGE = SOUP.get('per_page')
        TOTAL_RESULTS = int(PAGES) * int(PER_PAGE)

        return Page(doujins=DOUJINS,
                    total_results=TOTAL_RESULTS,
                    total_pages=PAGES,
                    per_page=PER_PAGE,
                    page=int(page))

    async def get_random(self) -> Doujin:
        """This method retrieves a random doujin.

        Args:

        Returns:
            Doujin: 
                dataclass with the doujin information within.
            
            You can access the dataclasses informations at `entities` package.
        """


        SOUP = await self._async_fetch(f'/random/')

        id = SOUP.find('h3', id='gallery_id').text.replace('#', '')

        doujin: Doujin = await self.get_doujin(id=id)
            
        return doujin

    async def search(self, query: str, sort: str=None, page: int=1) -> SearchPage:
        """This method retrieves the search page based on a query.

        Args:
            query str: 
                searchable term string. Ex: houshou marine, boa hancock, naruto
            sort str:
                doujin sort order
            page int:
                number of the page with results

        Returns:
            SearchPage: 
                dataclass with a list of DoujinThumbnail.
            
            You can access the dataclasses informations at `entities` package.
        """

        if query.isnumeric():
            any_doujin: Doujin = await self.get_doujin(id=query)
            if any_doujin is not None:
                return any_doujin

        sort = sort.value if isinstance(sort, Sort) else sort
        params = {'query': query, 'page': page, 'sort': sort} if sort is not None else {'query': query, 'page': page}

        SOUP = await self._async_fetch(urljoin(self._API_URL, f'galleries/search'), params=params, is_json=True)

        DOUJINS = [Doujin.from_json(json_object=doujin) for doujin in SOUP.get('result')]
        
        return SearchPage(query=query,
                          sort=sort,
                          total_results=SOUP.get('num_pages')*SOUP.get('per_page'),
                          total_pages=SOUP.get('num_pages'),
                          doujins=DOUJINS)
    
    async def search_pages(self,
                           query: str,
                           sort: str=None,
                           max_pages: int=1,
                           *, concurrent_tasks: int=3) -> AsyncGenerator[SearchPage, None]:
        TASKS = []
        
        for page in range(1, max_pages + 1):
            if len(TASKS) < concurrent_tasks:
                task = asyncio.ensure_future(self.search(query=query, sort=sort, page=page))
                TASKS.append(task)
            
            else:
                for task in TASKS:
                    yield await task
                
                TASKS = []
        
        # yield remaining tasks
        for task in TASKS:
            yield await task
    
    @Cache(max_age_seconds=3600, max_size=15, cache_key_position=1, cache_key_name='page').async_cache
    async def get_characters(self, page) -> CharacterListPage:
        """This method retrieves a list of characters that are available on NHentai site.

        Args:
            page: 
                number of the pagination page.

        Returns:
            CharacterListPage: 
                dataclass with the character list within.
            
            You can access the dataclasses informations at `entities` package.
        """

        SOUP = await self._async_fetch(f'/characters/?page={page}')
        
        pagination_section = SOUP.find('section', class_='pagination')
        TOTAL_PAGES = int(pagination_section.find('a', class_='last')['href'].split('=')[-1])
        CHARACTERS = []

        character_list_section = SOUP.find('div', class_='container')
        section = character_list_section.find_all('section')
        for link in section:
            for character in link:
                try:
                    TITLE = character.find('span', class_='name').text
                    CHARACTERS.append(CharacterLink(section=TITLE[0] if not TITLE[0].isnumeric() else '#',
                                                    title=TITLE,
                                                    url=character['href'],
                                                    total_entries=int(character.find('span', class_='count').text)))
                except Exception as err:
                    logging.error(err)
        
        return CharacterListPage(page=page,
                                 total_pages=int(TOTAL_PAGES),
                                 characters=CHARACTERS)

    async def get_popular_now(self):
        """This method retrieves a list of the current most popular doujins.

        Args:

        Returns:
            PopularPage: 
                dataclass with the current popular doujin list within.
            
            You can access the dataclasses informations at `entities` package.
        """

        SOUP = await self._async_fetch(f'/')
        
        popular_section = SOUP.find('div', class_='index-popular')

        DOUJINS_IDS = [item.find('a', class_='cover')['href'].split('/')[2] for item in popular_section.find_all('div', class_='gallery')]
        ROUTINES = [self.get_doujin(doujin_id) for doujin_id in DOUJINS_IDS]

        DOUJINS = await asyncio.gather(*ROUTINES)
        DOUJIN_LIST = list()

        for popular_doujin in DOUJINS:
            if popular_doujin is not None:
                DOUJIN_LIST.append(DoujinThumbnail(id=popular_doujin.id,
                                                media_id=popular_doujin.media_id,
                                                title=popular_doujin.title,
                                                languages=popular_doujin.languages,
                                                cover=popular_doujin.cover,
                                                url=urljoin(self._BASE_URL, f"/g/{popular_doujin.id}"),
                                                tags=popular_doujin.tags))
        
        return PopularPage(doujins=DOUJIN_LIST,
                           total_doujins=len(DOUJIN_LIST))

    # def get_artists(self, page: int = 1) -> ArtistListPage:
    #     raise NotImplementedError

    # def get_tags(self, page: int = 1) -> TagListPage:
    #     raise NotImplementedError

    # def get_groups(self, page: int = 1) -> GroupListPage:
    #     raise NotImplementedError
