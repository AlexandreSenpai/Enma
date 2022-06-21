from setuptools import setup
import os

def readme():
    with open('./README.md', 'r') as readme:
        return readme.read()

def make_setup(env_name: str, version: str):
    if env_name == 'prd':
        return setup(
            name='NHentai-API',
            version=version,
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
            packages=['Nhentai', 'NHentai.asynch', 'NHentai.sync', 'NHentai.core'],
            install_requires=['requests', 'beautifulsoup4', 'aiohttp', 'expiringdict', 'google-cloud-pubsub', 'google-auth'],
            include_package_data=True,
            zip_safe=False
        )
    return setup(
        name='dev-nhentai-build',
        version=version,
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
        packages=['dev_nhentai', 'dev_nhentai.asynch', 'dev_nhentai.sync', 'dev_nhentai.core'],
        install_requires=['requests', 'beautifulsoup4', 'aiohttp', 'expiringdict', 'google-cloud-pubsub', 'google-auth'],
        include_package_data=True,
        zip_safe=False
    )

if __name__ == '__main__':
    env = os.getenv('NHENTAI_ENVIRONMENT', 'dev')
    version = os.getenv('NHENTAI_VERSION', '0.0.0')
    print(f'TARGET_ENVIRONMENT: {env}\nTARGET_VERSION: {version}')
    make_setup(env, version)