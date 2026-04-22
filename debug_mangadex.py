
from enma.infra.adapters.repositories.mangadex import Mangadex
import json
import requests

def debug_mangadex():
    sut = Mangadex()
    manga_id = '65498ee8-3c32-4228-b433-73a4d08f8927'

    url = f'https://api.mangadex.org/manga/{manga_id}'
    resp = requests.get(url, params={'includes[]': ['cover_art', 'author', 'artist']})
    data = resp.json()

    attrs = data['data']['attributes']
    print(f"Title: {attrs.get('title')}")
    print(f"AltTitles: {json.dumps(attrs.get('altTitles'), indent=2)}")

if __name__ == "__main__":
    debug_mangadex()
