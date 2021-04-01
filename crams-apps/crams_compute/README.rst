=====
Crams Compute
=====

Crams Compute is a Django app to ...

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "crams_compute" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'crams_compute',
    ]

2. Include the crams_compute URLconf in your project urls.py like this::

    path('crams_compute/', include('crams_compute.urls')),

3. Run ``python manage.py migrate`` to create the models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/