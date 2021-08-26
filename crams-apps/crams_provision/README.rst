Crams Provision Package
=======================

Crams Provision is a Django app package for CRAMS api open source. Detailed documentation is in the "docs" directory.
Souce code is available at https://github.com/CRAMS-Dashboard/crams-api

Quick start
-----------

1. Add "crams_provision" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'crams_provision',
    ]

2. Include the crams_provision URLconf in your project urls.py like this::

    path('', include('crams_provision.urls')),