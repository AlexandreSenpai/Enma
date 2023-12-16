import requests


def default_downloader(uri: str, output_path: str) -> None:
    with open(output_path, 'wb') as f:
        for chunk in requests.get(uri, stream=True).iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)