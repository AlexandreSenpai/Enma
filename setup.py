from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='NHentai-API',
    version='0.0.14',
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
    keywords='nhentai hentai AlexandreSenpai',
    license='MIT',
    packages=['NHentai', 'NHentai.entities'],
    install_requires=['requests', 'beautifulsoup4'],
    include_package_data=True,
    zip_safe=False
)