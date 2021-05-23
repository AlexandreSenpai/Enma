import logging

from .base_wrapper import BaseWrapper
from .base_wrapper import (Doujin, 
                           DoujinThumbnail,
                           HomePage, 
                           SearchPage, 
                           TagListPage, 
                           GroupListPage, 
                           CharacterListPage, 
                           ArtistListPage, 
                           PopularPage,
                           CharacterLink) 

class NHentai(BaseWrapper):
    def get_doujin(self, id: str) -> Doujin:
        """This method receives a string id as parameter, 
        gets its informations and returns as a Doujin entity.
        """

        SOUP = self._fetch(f'/g/{id}/')

        info_box = SOUP.find('div', id='info')

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
        thumbs = SOUP.findAll('div', class_='thumb-container')

        for thumb in thumbs:
            img = thumb.find('img', class_='lazyload')['data-src']
            img_original_size = img.split('/')
            gallery_id = img_original_size[4]
            IMAGES.append(f'{self._IMAGE_BASE_URL}/{gallery_id}/{img_original_size[-1].replace("t", "")}')
        
        return Doujin(id=id,
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

        SOUP = self._fetch(f'/?page={page}')

        pagination_section = SOUP.find('section', class_='pagination')
        TOTAL_PAGES = int(pagination_section.find('a', class_='last')['href'].split('=')[-1])
        DOUJINS = []

        doujin_boxes = SOUP.find_all('div', class_='gallery')
        for item in doujin_boxes:
            DOUJIN_ID = item.find('a', class_='cover')['href'].split('/')[2]
            DOUJIN_TITLE = item.find('div', class_='caption').text
            DOUJIN_LANG = self._get_lang_by_title(DOUJIN_TITLE)
            DOUJIN_COVER = item.find('img', class_='lazyload')['data-src']
            DOUJIN_TAGS = item['data-tags'].split()

            DOUJINS.append(DoujinThumbnail(id=DOUJIN_ID,
                                           title=DOUJIN_TITLE,
                                           lang=DOUJIN_LANG,
                                           cover=DOUJIN_COVER,
                                           url=f"{self._BASE_URL}/g/{DOUJIN_ID}",
                                           data_tags=DOUJIN_TAGS))
        
        return HomePage(doujins=DOUJINS,
                        total_pages=TOTAL_PAGES)
    
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
        """This method retrieves a random doujin
        """

        SOUP = self._fetch(f'/random/')

        id = SOUP.find('h3', id='gallery_id').text.replace('#', '')

        doujin: Doujin = self.get_doujin(id=id)
            
        return doujin

    def search(self, query: str, sort: str=None, page: int=1) -> SearchPage:
        """This method retrieves the search page based on a query.
        """
        
        if query.isnumeric():
            any_doujin = self.get_doujin(id=query)
            if any_doujin is not None:
                return any_doujin

        if sort:
            SOUP = self._fetch(f'/search/?q={query}&page={page}&sort={sort}')
        else:
            SOUP = self._fetch(f'/search/?q={query}&page={page}')

        total_results = SOUP.find('div', id='content').find('h1').text.strip().split()[0]

        TOTAL_RESULTS = int(float(total_results.replace(',', '')))
        TOTAL_PAGES = 0
        DOUJINS = []

        pagination_section = SOUP.find('section', class_='pagination')
        if pagination_section is not None:
            last_page_HTMLObj = pagination_section.find('a', class_='last')
            if last_page_HTMLObj is not None:
                TOTAL_PAGES = int(last_page_HTMLObj['href'].split('&')[1][5:])
            else:
                last_page_HTMLObj = pagination_section.find('a', class_='page current')
                TOTAL_PAGES = int(last_page_HTMLObj['href'].split('&')[1][5:])

        doujin_boxes = SOUP.find_all('div', class_='gallery')
        for item in doujin_boxes:
            DOUJIN_ID = item.find('a', class_='cover')['href'].split('/')[2]
            DOUJIN_TITLE = item.find('div', class_='caption').text
            DOUJIN_LANG = self._get_lang_by_title(item.find('div', class_='caption').text)
            DOUJIN_COVER = item.find('img', class_='lazyload')['data-src']
            DOUJIN_TAGS = item['data-tags'].split()

            DOUJINS.append(DoujinThumbnail(id=DOUJIN_ID,
                                           title=DOUJIN_TITLE,
                                           lang=DOUJIN_LANG,
                                           cover=DOUJIN_COVER,
                                           url=f"{self._BASE_URL}/g/{DOUJIN_ID}",
                                           data_tags=DOUJIN_TAGS))
            
        return SearchPage(query=query,
                          sort=sort or 'recente',
                          total_results=TOTAL_RESULTS,
                          total_pages=TOTAL_PAGES,
                          doujins=DOUJINS)

    def get_characters(self, page: int = 1) -> CharacterListPage:
        """This method retrieves a list of characters that are available on NHentai site.
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
        """This method retrieves a list of the current most popular doujins
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
                                           url=f"{self._BASE_URL}/g/{DOUJIN_ID}",
                                           data_tags=item['data-tags'].split()))
        
        return PopularPage(doujins=DOUJINS,
                           total_doujins=len(DOUJINS))

    def get_artists(self, page: int = 1) -> ArtistListPage:
        raise NotImplementedError

    def get_tags(self, page: int = 1) -> TagListPage:
        raise NotImplementedError

    def get_groups(self, page: int = 1) -> GroupListPage:
        raise NotImplementedError
