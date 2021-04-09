from typing import Dict, List
import logging
import json

from bs4 import BeautifulSoup
import requests

from .entities.doujin import Doujin, DoujinThumbnail
from .entities.page import HomePage, SearchPage, TagListPage, GroupListPage, CharacterListPage, ArtistListPage
from .entities.links import CharacterLink 

class NHentai:
    def __init__(self):
        self._BASE_URL = 'https://nhentai.net'
        self._IMAGE_BASE_URL = 'https://i.nhentai.net/galleries'
        self._SUPORTED_LANG = {'English': 'english', 'Chinese': 'chinese'}
    
    def _get_lang_by_title(self, title: str) -> str:
        """This method runs through the title inputed and search by
        one of supported languages if it doesnt finds the methods returns
        Japanese.
        """

        acceptable_title = title.replace('[', '').replace(']', '')
        partitoned_title = acceptable_title.split(' ')

        lang = 'japanese'

        for part in partitoned_title:
            current_language_key = self._SUPORTED_LANG.get(part)
            lang = current_language_key if current_language_key is not None else lang 
        
        return lang


    def _get_doujin(self, id: str) -> Doujin:
        """This method receives a string id as parameter, 
        gets its informations and returns as a Doujin entity.
        """

        doujin_page = requests.get(f'{self._BASE_URL}/g/{id}/')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')

        info_box = soup.find('div', id='info')

        if info_box is None:
            return None

        title_section = info_box.find('h2', class_='title')
        
        TITLE = info_box.find('h1', class_='title').find('span', class_='pretty').text
        SECONDARY_TITLE = title_section.text if title_section is not None else ''
        IMAGES = []
        TAGS_TO_DICT = {}

        # Getting dinamically the doujin properties
        # This looping may return information as tags, artists, languages, categories and more.
        tags = info_box.find_all('div', class_='tag-container field-name')

        for item in tags:
            for i in item.find('span', class_='tags').find_all('a', class_='tag'):
            
                if TAGS_TO_DICT.get(item.text.strip().split()[0].lower().replace(':', '')) is None:
                    TAGS_TO_DICT[item.text.strip().split()[0].lower().replace(':', '')] = []

                TAGS_TO_DICT[item.text.strip().split()[0].lower().replace(':', '')].append(i.find('span', class_='name').text)            
        
        # Getting dinamically the doujin images
        # This looping gets the images id from its thumbs then uses it to create the page final url.
        thumbs = soup.findAll('div', class_='thumb-container')

        for thumb in thumbs:
            img = thumb.find('img', class_='lazyload')['data-src']
            img_original_size = img.split('/')
            gallery_id = img_original_size[4]
            IMAGES.append(f'{self._IMAGE_BASE_URL}/{gallery_id}/{img_original_size[-1].replace("t", "")}')
        
        return Doujin(
                        id=id,
                        title=TITLE,
                        secondary_title=SECONDARY_TITLE,
                        tags=TAGS_TO_DICT.get('tags', []),
                        artists=TAGS_TO_DICT.get('artists', []),
                        groups=TAGS_TO_DICT.get('groups', []),
                        languages=TAGS_TO_DICT.get('languages', []),
                        categories=TAGS_TO_DICT.get('categories', []),
                        characters=TAGS_TO_DICT.get('characters', []),
                        parodies=TAGS_TO_DICT.get('parodies', []),
                        images=IMAGES,
                        total_pages=len(IMAGES))

    def get_pages(self, page: int=1) -> HomePage:
        """This method paginates through the homepage of NHentai and returns the doujins
        initial information as id, title, language, cover and data-tags.
        """

        nhentai_homepage = requests.get(f'{self._BASE_URL}/?page={page}')
        soup = BeautifulSoup(nhentai_homepage.content, 'html.parser')

        pagination_section = soup.find('section', class_='pagination')
        TOTAL_PAGES = int(pagination_section.find('a', class_='last')['href'].split('=')[-1])
        DOUJINS = []

        doujin_boxes = soup.find_all('div', class_='gallery')
        for item in doujin_boxes:

            TITLE = item.find('div', class_='caption').text
            LANG = self._get_lang_by_title(TITLE)

            DOUJINS.append(DoujinThumbnail(
                                            id=item.find('a', class_='cover')['href'].split('/')[2],
                                            title=TITLE,
                                            lang=LANG,
                                            cover=item.find('img', class_='lazyload')['data-src'],
                                            data_tags=item['data-tags'].split()))
        
        return HomePage(
                        doujins=DOUJINS,
                        total_pages=TOTAL_PAGES)
    
    def get_user_page(self, uid: str, username: str) -> dict:
        
        """!!!!!DEPRECATED!!!!!
        """

        user_page = requests.get(f'{self._BASE_URL}/users/{uid}/{username}')
        soup = BeautifulSoup(user_page.content, 'html.parser')

        user_container = soup.find('div' ,id='user-container')

        profile_pic_url = user_container.find('img')['src']
        profile_username = user_container.find('h1').text
        profile_since = user_container.find('time').text

        favs_container = soup.find('div', id='recent-favorites-container')

        galleries = favs_container.find_all('div', class_='gallery')

        favs = []

        for gallery in galleries:
            favs.append({
                'id': gallery.find('a', class_='cover')['href'].split('/')[2],
                'cover': gallery.find('img')['data-src'],
                'title': gallery.find('div', class_='caption').text,
                'data-tags': gallery['data-tags'].split(' ')
            })

        return {
            'uid': uid,
            'username': profile_username,
            'image': profile_pic_url,
            'since': profile_since,
            'doujins': favs
        }

    def get_random(self) -> Doujin:
        """This method retrieves a random doujin
        """

        doujin_page = requests.get(f'{self._BASE_URL}/random/')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')

        id = soup.find('h3', id='gallery_id').text.replace('#', '')

        doujin: Doujin = self._get_doujin(id=id)
            
        return doujin

    def search(self, query: str, sort: str=None, page: int=1) -> SearchPage:
        """This method retrieves the search page based on a query.
        """
        
        if query.isnumeric():
            any_doujin = self._get_doujin(id=query)
            if any_doujin is not None:
                return any_doujin

        if sort:
            search_page = requests.get(f'{self._BASE_URL}/search/?q={query}&page={page}&sort={sort}')
        else:
            search_page = requests.get(f'{self._BASE_URL}/search/?q={query}&page={page}')

        soup = BeautifulSoup(search_page.content, 'html.parser')

        total_results = soup.find('div', id='content').find('h1').text.strip().split()[0]

        TOTAL_RESULTS = int(float(total_results.replace(',', '')))
        TOTAL_PAGES = 0
        DOUJINS = []

        pagination_section = soup.find('section', class_='pagination')
        if pagination_section is not None:
            last_page_HTMLObj = pagination_section.find('a', class_='last')
            if last_page_HTMLObj is not None:
                TOTAL_PAGES = int(last_page_HTMLObj['href'].split('&')[1][5:])
            else:
                last_page_HTMLObj = pagination_section.find('a', class_='page current')
                TOTAL_PAGES = int(last_page_HTMLObj['href'].split('&')[1][5:])

        doujin_boxes = soup.find_all('div', class_='gallery')
        for item in doujin_boxes:

            DOUJINS.append(DoujinThumbnail(
                                            id=item.find('a', class_='cover')['href'].split('/')[2],
                                            title=item.find('div', class_='caption').text,
                                            lang=self._get_lang_by_title(item.find('div', class_='caption').text),
                                            cover=item.find('img', class_='lazyload')['data-src'],
                                            data_tags=item['data-tags'].split()))
            
        return SearchPage(
                            query=query,
                            sort=sort or 'recente',
                            total_results=TOTAL_RESULTS,
                            total_pages=TOTAL_PAGES,
                            doujins=DOUJINS)

    def get_characters(self, page: int = 1) -> CharacterListPage:
        """This method retrieves a list of characters that are available on NHentai site.
        """

        character_page = requests.get(f'{self._BASE_URL}/characters/?page={page}')
        soup = BeautifulSoup(character_page.content, 'html.parser')

        pagination_section = soup.find('section', class_='pagination')
        TOTAL_PAGES = int(pagination_section.find('a', class_='last')['href'].split('=')[-1])
        CHARACTERS = []

        character_list_section = soup.find('div', class_='container')
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

    def get_artists(self, page: int = 1) -> ArtistListPage:
        raise NotImplementedError

    def get_tags(self, page: int = 1) -> TagListPage:
        raise NotImplementedError

    def get_groups(self, page: int = 1) -> GroupListPage:
        raise NotImplementedError

if __name__ == '__main__':
    nhentai = NHentai()
    test = nhentai.get_characters(page=32)
    print(test)
