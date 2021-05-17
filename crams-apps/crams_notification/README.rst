=====
Crams Notification
=====

Crams Notification is a Django app to ...

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "crams_notification" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'crams_notification',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('crams_notification/', include('crams_notification.urls')),

3. Run ``python manage.py migrate`` to create the crams_notification models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to manage your notification