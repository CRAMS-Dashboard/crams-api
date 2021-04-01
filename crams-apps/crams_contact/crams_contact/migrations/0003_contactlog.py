# Generated by Django 3.1.1 on 2021-03-09 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crams_log', '0002_userlog'),
        ('crams_contact', '0002_load_contact_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crams_contact_db_id', models.IntegerField(blank=True, null=True)),
                ('log_parent', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='contactlog', to='crams_log.cramslog')),
            ],
            options={
                'unique_together': {('crams_contact_db_id', 'log_parent')},
            },
        ),
    ]
