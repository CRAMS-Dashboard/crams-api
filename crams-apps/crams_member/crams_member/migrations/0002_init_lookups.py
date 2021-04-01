# coding=utf-8
"""

"""
from django.db import migrations


def load_crams_member_inital_data_from_sql():
    import os

    file_name = 'project_member_status.sql'
    sql_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sql_dir, file_name), 'r').read()

    return sql_statements


class Migration(migrations.Migration):

    dependencies = [
        ('crams_member', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(load_crams_member_inital_data_from_sql()),
    ]
