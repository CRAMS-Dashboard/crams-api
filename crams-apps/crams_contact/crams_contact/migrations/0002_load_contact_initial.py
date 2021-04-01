# Generated by Django 3.1.1 on 2020-11-20 01:05

import os

from django.db import migrations


def load_nectar_inital_data_from_sql():
    file_name = 'contact_initial.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()
    return sql_statements


class Migration(migrations.Migration):
    dependencies = [
        ('crams_contact', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(load_nectar_inital_data_from_sql()),
    ]
