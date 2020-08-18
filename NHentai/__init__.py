from bs4 import BeautifulSoup
import requests
import json

class NHentai:
    def __init__(self):
        self._BASE_URL = 'https://nhentai.net'
        self._IMAGE_BASE_URL = 'https://i.nhentai.net/galleries'
        self._SUPORTED_LANG = ['English', 'Chinese']
    
    def _get_lang_by_title(self, title: str) -> str:
        acceptable_title = title.replace('[', '').replace(']', '')
        partitoned_title = acceptable_title.split(' ')

        lang = 'Japanese'

        for part in partitoned_title:
            try:
                i = self._SUPORTED_LANG.index(part)
                lang = self._SUPORTED_LANG[i]
            except Exception as err:
                pass
        
        return lang


    def _get_doujin(self, id: str) -> dict:

        doujin_page = requests.get(f'{self._BASE_URL}/g/{id}/')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')

        return_object = {
            "id": id,
            "title": "",
            "secondary_title": "",
            "tags": [],
            "artists": [],
            "languages": [],
            "categories": [],
            "pages": 0,
            "pages": [],
            "images": []
        }

        info_box = soup.find('div', id='info')

        if info_box is None:
            return None

        return_object["title"] = info_box.find('h1', class_='title').find('span', class_='pretty').text
        return_object["secondary_title"] = title_section.text if (title_section := info_box.find('h2', class_='title')) is not None else ''

        tags = info_box.find_all('div', class_='tag-container field-name')
        for item in tags:
            try:
                for i in item.find('span', class_='tags').find_all('a', class_='tag'):
                    return_object[item.text.strip().split()[0].lower().replace(':', '')].append(i.find('span', class_='name').text)            
            except Exception as err:
                pass
        
        doujin_image = requests.get(f'{self._BASE_URL}/g/{id}/1')
        soup = BeautifulSoup(doujin_image.content, 'html.parser')

        first_url_string = soup.find('section', id='image-container').find('img')['src'].split('/')

        gallery_id = first_url_string[4]
        image_mime = first_url_string[-1].split('.')[-1]

        return_object['images'] = [f'{self._IMAGE_BASE_URL}/{gallery_id}/{page}.{image_mime}' for page in range(1, int(return_object['pages'][0]) + 1)]
            
        return return_object

    def get_pages(self, page: int=1) -> list:

        nhentai_homepage = requests.get(f'{self._BASE_URL}/?page={page}')
        soup = BeautifulSoup(nhentai_homepage.content, 'html.parser')

        return_object = {
            "doujins": [],
            "totalPages": 0
        }

        pagination_section = soup.find('section', class_='pagination')
        return_object['totalPages'] = int(pagination_section.find('a', class_='last')['href'].split('=')[-1])

        doujin_boxes = soup.find_all('div', class_='gallery')
        for item in doujin_boxes:

            title = item.find('div', class_='caption').text

            lang = self._get_lang_by_title(title)

            item_information = {
                "id": item.find('a', class_='cover')['href'].split('/')[2],
                "title": title,
                "lang": lang, 
                "cover": item.find('img', class_='lazyload')['data-src'],
                "data-tags": item['data-tags'].split(),
            }

            return_object['doujins'].append(item_information)
        
        return return_object
    
    def get_user_page(self, uid: str, username: str) -> dict:
        
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

    def get_random(self) -> dict:
    
        doujin_page = requests.get(f'{self._BASE_URL}/random/')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')

        id = soup.find('h3', id='gallery_id').text.replace('#', '')

        return_object: dict = self._get_doujin(id=id)
            
        return return_object

    def search(self, query: str, sort: str=None, page: int=1) -> dict:

        if query.isnumeric():
            any_doujin = self._get_doujin(id=query)
            if any_doujin is not None:
                return any_doujin

        if sort:
            search_page = requests.get(f'{self._BASE_URL}/search/?q={query}&page={page}&sort={sort}')
        else:
            search_page = requests.get(f'{self._BASE_URL}/search/?q={query}&page={page}')

        soup = BeautifulSoup(search_page.content, 'html.parser')

        return_object = {
            "query": query,
            "sort": sort or 'Recente',
            "totalResults": 0,
            "doujins": [],
            "totalPages": 0,
        }

        total_results = soup.find('div', id='content').find('h1').text.strip().split()[0]
        return_object['totalResults'] = int(float(total_results.replace(',', '')))

        pagination_section = soup.find('section', class_='pagination')
        if pagination_section is not None:
            last_page_HTMLObj = pagination_section.find('a', class_='last')
            if last_page_HTMLObj is not None:
                return_object['totalPages'] = int(last_page_HTMLObj['href'].split('&')[1][5:])
            else:
                last_page_HTMLObj = pagination_section.find('a', class_='page current')
                return_object['totalPages'] = int(last_page_HTMLObj['href'].split('&')[1][5:])

        doujin_boxes = soup.find_all('div', class_='gallery')
        for item in doujin_boxes:

            item_information = {
                "id": item.find('a', class_='cover')['href'].split('/')[2],
                "title": item.find('div', class_='caption').text,
                "lang": self._get_lang_by_title(item.find('div', class_='caption').text),
                "cover": item.find('img', class_='lazyload')['data-src'],
                "data-tags": item['data-tags'].split(),
            }

            return_object['doujins'].append(item_information)
            
        return return_object

if __name__ == '__main__':
    nhentai = NHentai()
    test = nhentai._get_doujin(id='30955')
    print(test)