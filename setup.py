from io import open
from setuptools import setup, find_packages


version = '1.1.3'
name = 'pypayment'


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=name,
    version=version,

    author='TimNekk',
    author_email='herew26@gmail.com',

    description=(
        'Payment providers API wrapper'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/TimNekk/pypayment',

    license='Apache License, Version 2.0, see LICENSE file',

    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    extras_require={
        'dev': [
            'environs==9.5.0',
            'pytest==7.0.1',
            'pytest-cov==3.0.0',
            'flake8==4.0.1',
            'mypy==0.961',
            'tox==3.25.0',
        ]
    },

    setuptools_git_versioning={
        "enabled": True,
    },
    setup_requires=["setuptools-git-versioning"],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
