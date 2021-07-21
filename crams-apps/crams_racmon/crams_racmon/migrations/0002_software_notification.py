import os

from django.db import migrations


def load_software_notications_from_sql():
    file_name = 'software_notification_templates.sql'
    sqls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sqls'))
    sql_statements = open(os.path.join(sqls_dir, file_name), 'r').read()

    return sql_statements

class Migration(migrations.Migration):
    dependencies = [
        ('crams_racmon', '0001_initial'),
        ('crams', '0011_softwarelicensestatus'),
    ]

    operations = [
        migrations.RunSQL(load_software_notications_from_sql()),
    ]