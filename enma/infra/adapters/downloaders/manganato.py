import requests

def manganato_downloader(uri: str, output_path: str) -> None:
    with open(output_path, 'wb') as f:
        for chunk in requests.get(url=uri, 
                                  stream=True, 
                                  headers={'Referer': 'https://chapmanganato.com/'}).iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)