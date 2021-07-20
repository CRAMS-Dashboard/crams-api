# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db import connection


def load_software_product_inital_data_from_sql():
    import os

    file_name = 'software_initial.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()

    return sql_statements


class Migration(migrations.Migration):
    dependencies = [
        ('crams_software', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(load_software_product_inital_data_from_sql()),
    ]