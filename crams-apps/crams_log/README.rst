Crams Log Package
===================

Crams Log is a Django app package for CRAMS api open source. Detailed documentation is in the "docs" directory.
Souce code is available at https://github.com/CRAMS-Dashboard/crams-api

Quick start
-------------

1. Add "crams_log" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'crams_log',
    ]

2. Include the crams_log URLconf in your project urls.py like this::

    path('', include('crams_log.urls')),
