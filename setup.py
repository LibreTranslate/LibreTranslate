#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    version='1.2.5',
    name='libretranslate',
    license='GNU Affero General Public License v3.0',
    description='Free and Open Source Machine Translation API. Self-hosted, no limits, no ties to proprietary services.',
    author='LibreTranslate Authors',
    author_email='pt@uav4geo.com',
    url='https://libretranslate.com',
    packages=find_packages(),
    # packages=find_packages(include=['openpredict']),
    # package_dir={'openpredict': 'openpredict'},
    package_data={'': ['static/*', 'static/**/*', 'templates/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'libretranslate=app.main:main',
            'ltmanage=app.manage:manage'
        ],
    },

    python_requires='>=3.6.0',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=open("requirements.txt", "r").readlines(),
    tests_require=['pytest==5.2.0'],
    setup_requires=['pytest-runner'],
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3 ",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ]
)
