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
        packages=['NHentai',
                  'NHentai.core',
                  'NHentai.core.auth',
                  'NHentai.core.auth.google',
                  'NHentai.core.helpers',
                  'NHentai.core.interfaces',
                  'NHentai.asynch',
                  'NHentai.asynch.infra',
                  'NHentai.asynch.infra.entrypoints',
                  'NHentai.asynch.infra.adapters',
                  'NHentai.asynch.infra.adapters.request',
                  'NHentai.asynch.infra.adapters.request.http',
                  'NHentai.asynch.infra.adapters.request.http.interfaces',
                  'NHentai.asynch.infra.adapters.request.http.implementations',
                  'NHentai.asynch.infra.adapters.repositories',
                  'NHentai.asynch.infra.adapters.repositories.hentai',
                  'NHentai.asynch.infra.adapters.repositories.hentai.implementations',
                  'NHentai.asynch.infra.adapters.brokers',
                  'NHentai.asynch.infra.adapters.brokers.implementations',
                  'NHentai.asynch.application',
                  'NHentai.asynch.application.use_cases',
                  'NHentai.asynch.infra.entrypoints.lib',
                  'NHentai.sync',
                  'NHentai.sync.infra',
                  'NHentai.sync.infra.entrypoints',
                  'NHentai.sync.infra.adapters',
                  'NHentai.sync.infra.adapters.request',
                  'NHentai.sync.infra.adapters.request.http',
                  'NHentai.sync.infra.adapters.request.http.interfaces',
                  'NHentai.sync.infra.adapters.request.http.implementations',
                  'NHentai.sync.infra.adapters.repositories',
                  'NHentai.sync.infra.adapters.repositories.hentai',
                  'NHentai.sync.infra.adapters.repositories.hentai.implementations',
                  'NHentai.sync.infra.adapters.brokers',
                  'NHentai.sync.infra.adapters.brokers.implementations',
                  'NHentai.sync.application',
                  'NHentai.sync.application.use_cases',
                  'NHentai.sync.infra.entrypoints.lib'],
        install_requires=['requests', 'beautifulsoup4', 'aiohttp', 'expiringdict', 'google-cloud-pubsub', 'google-auth'],
        include_dirs=True,
        include_package_data=True,
        zip_safe=False
    )

if __name__ == '__main__':
    env = os.getenv('NHENTAI_ENVIRONMENT', 'dev')
    version = os.getenv('NHENTAI_VERSION', '0.0.15')
    print(f'TARGET_ENVIRONMENT: {env}\nTARGET_VERSION: {version}')
    make_setup(env, version)