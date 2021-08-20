=====
Crams RacMon
=====

Crams RacMon is a Django app to ...

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "crams_demo" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'crams_demo',
    ]

2. Include the crams_demo URLconf in your project urls.py like this::

    path('crams_demo/', include('crams_demo.urls')),

3. Run ``python manage.py migrate`` to create the crams_demo models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a crams_demo (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/crams_demo/ to participate in the crams_demo.