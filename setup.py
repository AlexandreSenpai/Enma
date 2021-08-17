from setuptools import setup
import os

def readme():
    with open('README.md') as f:
        return f.read()

env = os.getenv('environment_name') or 'dev'

if env == 'prd':
    setup(
        name='NHentai-API',
        version='0.0.16',
        description='NHentai Python API made using webscraping.',
        long_description=readme(),
        long_description_content_type='text/markdown',
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        url='https://github.com/AlexandreSenpai/NHentai-API',
        author='AlexandreSenpai',
        author_email='alexandrebsramos@hotmail.com',
        keywords='Tagshentai, nhentai, nhentai.net, API, NSFW',
        license='MIT',
        packages=['NHentai', 'NHentai.entities', 'NHentai.utils'],
        install_requires=['requests', 'beautifulsoup4', 'aiohttp', 'expiringdict'],
        include_package_data=True,
        zip_safe=False
    )
elif env == 'dev':
    setup(
        name='dev-nhentai-build',
        version='0.0.5',
        description='NHentai Python API made using webscraping.',
        long_description=readme(),
        long_description_content_type='text/markdown',
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        url='https://github.com/AlexandreSenpai/NHentai-API',
        author='AlexandreSenpai',
        author_email='alexandrebsramos@hotmail.com',
        keywords='Tagshentai, nhentai, nhentai.net, API, NSFW',
        license='MIT',
        packages=['dev_nhentai', 'dev_nhentai.entities', 'dev_nhentai.utils'],
        install_requires=['requests', 'beautifulsoup4', 'aiohttp', 'expiringdict'],
        include_package_data=True,
        zip_safe=False
    )