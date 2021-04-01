# Generated by Django 3.1.1 on 2021-02-02 04:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crams_contact', '0002_load_contact_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('contact', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='crams_contact.contact')),
            ],
        ),
        migrations.CreateModel(
            name='OrganisationManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='manager_organisations', to='crams_contact.contact')),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='organisation_managers', to='crams_contact.organisation')),
            ],
            options={
                'unique_together': {('contact', 'organisation')},
            },
        ),
        migrations.CreateModel(
            name='FacultyManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='manager_faculties', to='crams_contact.contact')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='faculty_managers', to='crams_contact.faculty')),
            ],
            options={
                'unique_together': {('contact', 'faculty')},
            },
        ),
        migrations.CreateModel(
            name='DepartmentManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='manager_departments', to='crams_contact.contact')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='department_managers', to='crams_contact.department')),
            ],
            options={
                'unique_together': {('contact', 'department')},
            },
        ),
    ]
