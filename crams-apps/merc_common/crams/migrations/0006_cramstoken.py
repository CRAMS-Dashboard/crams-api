# Generated by Django 3.1.1 on 2020-11-24 23:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authtoken', '0002_auto_20160226_1747'),
        ('crams', '0005_support'),
    ]

    operations = [
        migrations.CreateModel(
            name='CramsToken',
            fields=[
                ('token_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='authtoken.token')),
                ('ks_roles', models.TextField(blank=True, null=True)),
            ],
            bases=('authtoken.token',),
        ),
    ]