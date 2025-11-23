# -*- coding: utf-8 -*- 

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()
    

REQUIREMENTS=[
    'PyYAML',
    'PyPDF2',
    'reportlab',
    'Pillow',
    'matplotlib',
    'paramiko',
    'pylatexenc',
    'markdown2',
]

NAME = 'YoungLion'
VERSION = '0.0.9.8'
DESCRIPTION = "It is a library whose main purpose is to make the work of YoungLion developers easier."
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
# URL = 'https://github.com/Cavanshirpro/YoungLion'
AUTHOR = "Cavanşir Qurbanzadə"
AUTHOR_EMAIL = "cavanshirpro@gmail.com"
LICENSE = 'MIT'
KEYWORDS = 'YoungLion, Young Lion, Cavanshirpro'

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    keywords=KEYWORDS,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    # url="https://github.com/Cavanshirpro/YoungLion",
    packages=find_packages('src'),
    install_requires=REQUIREMENTS,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        'YoungLion': ['static/*']
    },
    package_dir={'': 'src'}
)