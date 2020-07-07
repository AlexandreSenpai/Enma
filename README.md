#NHentai API
##An API made using python webscrapping

Library Features:

Home page pagination,
Doujin information,
Random doujin

API

from NHentai import NHentai

if __name__ == '__main__':
    nhentai = NHentai()
    dict: random_doujin = nhentai.get_random()