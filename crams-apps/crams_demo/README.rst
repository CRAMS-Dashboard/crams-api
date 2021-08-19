=====
Crams RacMon
=====

Crams RacMon is a Django app to ...

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "crams_racmon" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'crams_racmon',
    ]

2. Include the crams_racmon URLconf in your project urls.py like this::

    path('crams_racmon/', include('crams_racmon.urls')),

3. Run ``python manage.py migrate`` to create the crams_racmon models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a crams_racmon (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/crams_racmon/ to participate in the crams_racmon.