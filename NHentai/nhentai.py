import json
from typing import Optional
from urllib.parse import urljoin
import logging

from .base_wrapper import BaseWrapper
from .entities.doujin import Doujin, DoujinThumbnail, Title, Tag, Page, Cover
from .entities.page import (HomePage, 
                            SearchPage, 
                            TagListPage, 
                            GroupListPage, 
                            CharacterListPage, 
                            ArtistListPage, 
                            PopularPage)
from .entities.links import CharacterLink 
from .entities.options import Sort

class NHentai(BaseWrapper):
    def get_doujin(self, id: str) -> Doujin:
        """This method fetches a doujin information based on id.

        Args:
            id: 
                Id of the target doujin.

        Returns:
            Doujin: 
                dataclass with the doujin information within.
            
            You can access the dataclasses informations at `entities` package.
        """

        if not id.isnumeric() or id[0] == '0':
            return None

        SOUP = self._fetch(urljoin(self._API_URL, f'gallery/{id}'), is_json=True)

        if SOUP.get('error'):
            return None

        MEDIA_ID = SOUP.get('media_id')

        ALL_TAGS = SOUP.get('tags')

        TAG_DICT = {'tag': [],
                    'artist': [],
                    'group': [],
                    'parody': [],
                    'character': [],
                    'category': [],
                    'language': []}
        
        for tag in ALL_TAGS:
                if TAG_DICT.get(TAG_TYPE := tag.get('type')) is not None:
                    TAG_DICT[TAG_TYPE].append(Tag.from_json(tag))
        
        PAGES = [Page.from_json(page, index, MEDIA_ID)
                 for index, page in enumerate(SOUP.get('images').get('pages'))]
        
        return Doujin(id=id,
                      title=Title.from_json(SOUP),
                      tags=TAG_DICT['tag'],
                      artists=TAG_DICT['artist'],
                      groups=TAG_DICT['group'],
                      languages=TAG_DICT['language'],
                      categories=TAG_DICT['category'],
                      characters=TAG_DICT['character'],
                      parodies=TAG_DICT['parody'],
                      images=PAGES,
                      total_pages=len(PAGES))

    def get_pages(self, page: int=1) -> HomePage:
        """This method paginates through the homepage of NHentai and returns the doujins.

        Args:
            page: 
                number of the pagination page.

        Returns:
            HomePage: 
                dataclass with a list of DoujinThumbnail.
            
            You can access the dataclasses informations at `entities` package.
        """

        SOUP = self._fetch(urljoin(self._API_URL, f'galleries/all?page={page}'), is_json=True)

        DOUJINS = [DoujinThumbnail.from_json(json_obj) for json_obj in SOUP.get('result')]

        return HomePage(doujins=DOUJINS,
                        total_pages=SOUP.get('num_pages'),
                        per_page=SOUP.get('per_page'),
                        page=page)
    
    def get_user_page(self, uid: str, username: str) -> dict:
        
        """!!!!!DEPRECATED!!!!!
        """

        SOUP = self._fetch(f'/users/{uid}/{username}')

        user_container = SOUP.find('div' ,id='user-container')

        profile_pic_url = user_container.find('img')['src']
        profile_username = user_container.find('h1').text
        profile_since = user_container.find('time').text

        favs_container = SOUP.find('div', id='recent-favorites-container')

        galleries = favs_container.find_all('div', class_='gallery')

        favs = []

        for gallery in galleries:
            favs.append({'id': gallery.find('a', class_='cover')['href'].split('/')[2],
                         'cover': gallery.find('img')['data-src'],
                         'title': gallery.find('div', class_='caption').text,
                         'data-tags': gallery['data-tags'].split(' ')})

        return {
            'uid': uid,
            'username': profile_username,
            'image': profile_pic_url,
            'since': profile_since,
            'doujins': favs
        }

    def get_random(self) -> Doujin:
        """This method retrieves a random doujin.

        Args:

        Returns:
            Doujin: 
                dataclass with the doujin information within.
            
            You can access the dataclasses informations at `entities` package.
        """


        SOUP = self._fetch(f'/random/')

        id = SOUP.find('h3', id='gallery_id').text.replace('#', '')

        doujin: Doujin = self.get_doujin(id=id)
            
        return doujin

    def search(self, query: str, page: int=1, sort: Optional[Sort]=Sort.RECENT) -> SearchPage:
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
        
        sort = sort.value if isinstance(sort, Sort) else sort
        print(urljoin(self._API_URL, f'galleries/search?query={query}&page={page}&sort={sort}'))

        SOUP = self._fetch(urljoin(self._API_URL, f'galleries/search?query={query}&page={page}&sort={sort}'), is_json=True)

        print(json.dumps(SOUP, indent=4))

        # if query.isnumeric():
        #     any_doujin: Doujin = self.get_doujin(id=query)
        #     if any_doujin is not None:
        #         return any_doujin

        # SOUP = self._fetch(f'/search/?q={query}&page={page}&sort={sort}')

        # total_results = SOUP.find('div', id='content').find('h1').text.strip().split()[0]

        # TOTAL_RESULTS = int(float(total_results.replace(',', '')))
        # TOTAL_PAGES = 0
        # DOUJINS = list()

        # pagination_section = SOUP.find('section', class_='pagination')
        # if pagination_section is not None:
        #     last_page_HTMLObj = pagination_section.find('a', class_='last')
        #     if last_page_HTMLObj is not None:
        #         TOTAL_PAGES = int(last_page_HTMLObj['href'].split('&')[1][5:])
        #     else:
        #         last_page_HTMLObj = pagination_section.find('a', class_='page current')
        #         TOTAL_PAGES = int(last_page_HTMLObj['href'].split('&')[1][5:])

        # doujin_boxes = SOUP.find_all('div', class_='gallery')
        # for item in doujin_boxes:
        #     DOUJIN_ID = item.find('a', class_='cover')['href'].split('/')[2]
        #     DOUJIN_TITLE = item.find('div', class_='caption').text
        #     DOUJIN_LANG = self._get_lang_by_title(item.find('div', class_='caption').text)
        #     DOUJIN_COVER = item.find('img', class_='lazyload')['data-src']
        #     DOUJIN_TAGS = item['data-tags'].split()

        #     DOUJINS.append(DoujinThumbnail(id=DOUJIN_ID,
        #                                    title=DOUJIN_TITLE,
        #                                    lang=DOUJIN_LANG,
        #                                    cover=DOUJIN_COVER,
        #                                    url=urljoin(self._BASE_URL, f"/g/{DOUJIN_ID}"),
        #                                    data_tags=DOUJIN_TAGS))
            
        # return SearchPage(query=query,
        #                   sort=sort,
        #                   total_results=TOTAL_RESULTS,
        #                   total_pages=TOTAL_PAGES,
        #                   doujins=DOUJINS)

    def get_characters(self, page: int = 1) -> CharacterListPage:
        """This method retrieves a list of characters that are available on NHentai site.

        Args:
            page: 
                number of the pagination page.

        Returns:
            CharacterListPage: 
                dataclass with the character list within.
            
            You can access the dataclasses informations at `entities` package.
        """

        SOUP = self._fetch(f'/characters/?page={page}')
        
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
    
    def get_popular_now(self):
        """This method retrieves a list of the current most popular doujins.

        Args:

        Returns:
            PopularPage: 
                dataclass with the current popular doujin list within.
            
            You can access the dataclasses informations at `entities` package.
        """

        SOUP = self._fetch(f'/')
        
        popular_section = SOUP.find('div', class_='index-popular')
        DOUJINS = []

        for item in popular_section.find_all('div', class_='gallery'):
            DOUJIN_TITLE = item.find('div', class_='caption').text
            DOUJIN_LANG = self._get_lang_by_title(DOUJIN_TITLE)
            DOUJIN_ID = item.find('a', class_='cover')['href'].split('/')[2]
            DOUJIN_COVER = item.find('img', class_='lazyload')['data-src']

            DOUJINS.append(DoujinThumbnail(id=DOUJIN_ID,
                                           title=DOUJIN_TITLE,
                                           lang=DOUJIN_LANG,
                                           cover=DOUJIN_COVER,
                                           url=urljoin(self._BASE_URL, f"/g/{DOUJIN_ID}"),
                                           data_tags=item['data-tags'].split()))
        
        return PopularPage(doujins=DOUJINS,
                           total_doujins=len(DOUJINS))

    def get_artists(self, page: int = 1) -> ArtistListPage:
        raise NotImplementedError

    def get_tags(self, page: int = 1) -> TagListPage:
        raise NotImplementedError

    def get_groups(self, page: int = 1) -> GroupListPage:
        raise NotImplementedError
