# coding=utf-8
""" The setup module for merc_common module

"""

from codecs import open
from setuptools import (setup, find_packages)
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='merc_common',

    version='1.0.0',

    description='Common core models for Monash University eResearch Projects',
    long_description=long_description,

    url='https://https://github.com/merc_common',

    author='Rafi M Feroze',
    author_email='mohamed.feroze+merc_common@monash.edu',

    license='Apache 2.0',

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Framework :: Django :: 3.1',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='monash eresearch crams',

    packages=find_packages(),

    install_requires=['django-filter',
                      'djangorestframework',
                      'django-rest-auth',
                      'python-dateutil',
                      'pytz',
                      'pyyaml',
                      'uritemplate',
                      ],
    include_package_data=True,
)
