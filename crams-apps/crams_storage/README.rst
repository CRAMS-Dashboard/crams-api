=====
Crams storage
=====

Crams Storage is a Django app to ...

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "crams_storage" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'crams_storage',
    ]

2. Include the crams_storage URLconf in your project urls.py like this::

    path('crams_storage/', include('crams_storage.urls')),

3. Run ``python manage.py migrate`` to create the models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/