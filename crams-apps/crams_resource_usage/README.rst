Crams Resource Usage Package
============================

Crams Resource Usage is a Django app package for CRAMS api open source. Detailed documentation is in the "docs" directory.
Souce code is available at https://github.com/CRAMS-Dashboard/crams-api

Quick start
-----------

1. Add "crams_resource_usage" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'crams_resource_usage',
    ]

2. Include the crams_resource_usage URLconf in your project urls.py like this::

    path('', include('crams_resource_usage.urls')),
