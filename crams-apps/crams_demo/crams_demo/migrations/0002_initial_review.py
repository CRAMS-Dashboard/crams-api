import os

from django.db import migrations


def load_demo_init_review_sql():
    file_name = 'review_init.mysql.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()
    return sql_statements


class Migration(migrations.Migration):
    dependencies = [
        ('crams_demo', '0002_software_notification'),
        ('crams_review', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(load_demo_init_review_sql())
    ]