from setuptools import setup, find_packages

def readme():
    with open('./README.md', 'r') as readme:
        return readme.read()

def make_setup():
    return setup(
        name='Enma',
        version="2.0.2",
        description='Enma is a Python library designed to fetch manga and doujinshi data from various sources.',
        long_description=readme(),
        long_description_content_type='text/markdown',
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        url='https://github.com/AlexandreSenpai/Enma',
        author='AlexandreSenpai',
        author_email='alexandrebsramos@hotmail.com',
        keywords='Tags, hentai, nhentai, nhentai.net, API, NSFW, erohoshi, Manganato, Doujinshi, Manga, Scrapper',
        license='MIT',
        packages=find_packages(),
        install_requires=['requests', 'beautifulsoup4'],
        include_package_data=True,
        zip_safe=False
    )

if __name__ == '__main__':
    make_setup()