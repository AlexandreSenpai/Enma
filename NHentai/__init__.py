from bs4 import BeautifulSoup
import requests

class NHentai:
    def __init__(self):
        self.__BASE_URL = 'https://nhentai.net'
        self.__IMAGE_BASE_URL = 'https://i.nhentai.net/galleries'
        self.__SUPORTED_LANG = ['English', 'Chinese']
    
    def __get_lang_by_title(self, title: str) -> str:
        acceptable_title = title.replace('[', '').replace(']', '')
        partitoned_title = acceptable_title.split(' ')

        lang = 'Japanese'

        for part in partitoned_title:
            try:
                i = self.__SUPORTED_LANG.index(part)
                lang = self.__SUPORTED_LANG[i]
            except:
                pass
        
        return lang

    def get_pages(self, page=1):

        nhentai_homepage = requests.get(f'{self.__BASE_URL}/?page={page}')
        soup = BeautifulSoup(nhentai_homepage.content, 'html.parser')

        return_object = {
            "doujins": [],
            "totalPages": 0
        }

        pagination_section = soup.find('section', class_='pagination')
        return_object['totalPages'] = pagination_section.find('a', class_='last')['href'].split('=')[-1]

        doujin_boxes = soup.find_all('div', class_='gallery')
        for item in doujin_boxes:

            title = item.find('div', class_='caption').text

            lang = self.__get_lang_by_title(title)

            item_information = {
                "id": item.find('a', class_='cover')['href'].split('/')[2],
                "title": title,
                "lang": lang, 
                "cover": item.find('img', class_='lazyload')['data-src'],
                "data-tags": item['data-tags'].split(),
            }

            return_object['doujins'].append(item_information)
        
        return return_object
    
    def get_doujin(self, id):

        doujin_page = requests.get(f'{self.__BASE_URL}/g/{id}/')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')

        return_object = {
            "id": id,
            "title": "",
            "tags": [],
            "artists": [],
            "languages": [],
            "categories": [],
            "pages": 0,
            "pages": [],
            "images": []
        }

        info_box = soup.find('div', id='info')
        return_object["title"] = info_box.find('h1', class_='title').find('span', class_='pretty').text

        tags = info_box.find_all('div', class_='tag-container field-name')
        for item in tags:
            try:
                for i in item.find('span', class_='tags').find_all('a', class_='tag'):
                    return_object[item.text.strip().split()[0].lower().replace(':', '')].append(i.find('span', class_='name').text)            
            except:
                pass
        
        doujin_image = requests.get(f'{self.__BASE_URL}/g/{id}/1')
        soup = BeautifulSoup(doujin_image.content, 'html.parser')
        gallery_id = soup.find('section', id='image-container').find('img')['src'].split('/')[4]
        return_object['images'] = [f'{self.__IMAGE_BASE_URL}/{gallery_id}/{page}.jpg' for page in range(1, int(return_object['pages'][0]) + 1)]
            
        return return_object

    def get_random(self):

        doujin_page = requests.get(f'{self.__BASE_URL}/random/')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')

        id = soup.find('h3', id='gallery_id').text.replace('#', '')

        return_object = {
            "id": id,
            "title": "",
            "tags": [],
            "artists": [],
            "languages": [],
            "categories": [],
            "pages": 0,
            "pages": [],
            "images": []
        }

        info_box = soup.find('div', id='info')
        return_object["title"] = info_box.find('h1', class_='title').find('span', class_='pretty').text

        tags = info_box.find_all('div', class_='tag-container field-name')
        for item in tags:
            try:
                for i in item.find('span', class_='tags').find_all('a', class_='tag'):
                    return_object[item.text.strip().split()[0].lower().replace(':', '')].append(i.find('span', class_='name').text)            
            except:
                pass
        
        doujin_image = requests.get(f'{self.__BASE_URL}/g/{id}/1')
        soup = BeautifulSoup(doujin_image.content, 'html.parser')
        gallery_id = soup.find('section', id='image-container').find('img')['src'].split('/')[4]
        return_object['images'] = [f'{self.__IMAGE_BASE_URL}/{gallery_id}/{page}.jpg' for page in range(1, int(return_object['pages'][0]) + 1)]
            
        return return_object

if __name__ == '__main__':
    nhentai = NHentai()
    test = nhentai.get_random()
    print(test)