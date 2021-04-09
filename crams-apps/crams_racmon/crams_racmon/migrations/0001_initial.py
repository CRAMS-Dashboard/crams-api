# Generated by Django 3.1.1 on 2021-03-16 03:37
import os

from django.db import migrations


def load_racmon_data_from_sql():
    file_name = 'racmon_initial.mysql.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()

    return sql_statements


def load_racmon_questions_from_sql():
    file_name = 'racmon_questions.mysql.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()

    return sql_statements


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.RunSQL(load_racmon_data_from_sql()),
        migrations.RunSQL(load_racmon_questions_from_sql()),
    ]