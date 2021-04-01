# Generated by Django 3.1.1 on 2020-11-20 01:02

import os

from django.db import migrations


def load_for_code_data_from_sql():
    file_name = 'for_code.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()
    return sql_statements


def load_seo_code_data_from_sql():
    file_name = 'seo_code.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()

    return sql_statements


def load_nectar_inital_data_from_sql():
    file_name = 'crams_initial.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()

    return sql_statements


def load_zone_data_from_sql():
    file_name = 'zones.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()
    return sql_statements


class Migration(migrations.Migration):
    dependencies = [
        ('crams', '0007_costunittype_zone'),
    ]

    operations = [
        migrations.RunSQL(load_nectar_inital_data_from_sql()),
        migrations.RunSQL(load_for_code_data_from_sql()),
        migrations.RunSQL(load_seo_code_data_from_sql()),
        migrations.RunSQL(load_zone_data_from_sql()),
    ]
