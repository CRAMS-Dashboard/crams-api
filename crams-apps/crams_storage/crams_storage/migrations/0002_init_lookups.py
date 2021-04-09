# Generated by Django 3.1.1 on 2020-11-20 00:54

from django.db import migrations


def load_crams_storage_inital_data_from_sql():
    from crams_storage.settings import BASE_DIR
    import os

    file_name = 'crams_storage/sqls/initial_storage.sql'
    sql_statements = open(os.path.join(BASE_DIR, file_name), 'r').read()

    return sql_statements


class Migration(migrations.Migration):

    dependencies = [
        ('crams_storage', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(load_crams_storage_inital_data_from_sql()),
    ]