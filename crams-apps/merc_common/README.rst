Merc Common Package
===================

Merc Common is a Django app common package for CRAMS api open source. Detailed documentation is in the "docs" directory.
Souce code is available at https://github.com/CRAMS-Dashboard/crams-api

Quick start
-----------

1. Add "merc_common" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'merc_common',
    ]

2. Include the merc_common URLconf in your project urls.py like this::

    path('', include('merc_common.urls')),
