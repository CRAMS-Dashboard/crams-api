Crams API
==========

Crams API is a Django application which integrated with all crams modulars.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "all crams modulars" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'merc_common',
        'crams_log',
        ...
    ]

2. Include the all crams modulars URLconf in your project urls.py like this::

    path('', include('merc_common.urls')),
    path('', include('crams_contact.urls')),

    ...

3. Run ``python manage.py migrate`` to create the crams api models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to see crams (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000 to test CRAMS Api.