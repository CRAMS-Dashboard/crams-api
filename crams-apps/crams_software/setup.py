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
    name='crams_software',

    version='1.0.0',

    description='software allocation related module for Crams project',
    long_description=long_description,

    url='https://https://github.com/crams_software',

    author='Rafi M Feroze',
    author_email='mohamed.feroze+crams_software@monash.edu',

    license='Apache 2.0',

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Framework :: Django :: 3.2',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='monash eresearch crams software',

    packages=find_packages(),

    install_requires=['merc-common==1.0.0',
                      'crams_log==1.0.0',
                      'crams_contact==1.0.0'
                      ],
    include_package_data=True,
)
