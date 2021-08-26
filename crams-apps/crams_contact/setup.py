#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine
#
# Commands:
# ### build source distribute:
#
# python setup.py dist
#
# ### publish package to PyPi
#
# python setup.py publish
#
# Note : make sure the .pypirc file is created in your home directory:
# #############################
#
# [distutils]
# index-servers =
#          pypi
#
# [pypi]
# repository = https://upload.pypi.org/legacy/
# username = <pypi_username>
# password = <pypi_password>
#
##################################
#
#

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'crams_contact'
VERSION = '1.0.0'
DESCRIPTION = 'CRAMS API opensource crams_contact package.'
URL = 'https://github.com/CRAMS-Dashboard/crams-api'
AUTHOR = 'Monash University e-Research Centre'
EMAIL = 'crams@monash.edu'

REQUIRES_PYTHON = '>=3.8.0'

# What packages are required for this module to be executed?
REQUIRED = [
    'merc-common>=1.0.0',
    'crams_log>=1.0.0',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# get the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(current_dir, 'README.rst'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# define the version number in __init__.py file
#  eg:
# __version__ = '1.0.0'
#
# Load the package's __init__.py module as a dictionary.
#
about = {}
# project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
# with open(os.path.join(current_dir, project_slug, '__init__.py')) as vf:
#     exec(vf.read(), about)
with open(os.path.join(current_dir, 'version.py'))as fv:
    exec(fv.read(), about)

current_version = about.get('__version__', None)
if not current_version:
    about['__version__'] = VERSION


def status(s):
    """Prints things in bold."""
    print('\033[1m{0}\033[0m'.format(s))


class DistributeSource(Command):
    """ python setup.py dist."""

    description = 'Build the package.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            status('Removing previous build dir ...')
            rmtree(os.path.join(current_dir, 'build'))

            status('Removing previous dist dir ...')
            rmtree(os.path.join(current_dir, 'dist'))
        except OSError:
            pass
        status('Building Source and Wheel (universal) distribution ...')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))
        sys.exit()


class PublishDist(Command):
    """Support setup.py upload."""

    description = 'Publish the package.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        status('Uploading the package to PyPI via Twine ...')
        os.system('twine upload dist/*')
        #
        # status('Pushing git tags…')
        # os.system('git tag v{0}'.format(about['__version__']))
        # os.system('git push --tags')
        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),

    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },

    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='GNU General Public License v3.0',
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django :: 3.2',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    # setup.py dist and publish
    cmdclass={
        'dist': DistributeSource,
        'publish': PublishDist,
    },
)
