# Generated by Django 3.1.1 on 2021-03-09 09:49

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crams', '0008_load_crams_lookups'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crams_contact', '0003_contactlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=9999)),
                ('notes', models.TextField(blank=True, max_length=1024, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='project_created_by', to=settings.AUTH_USER_MODEL)),
                ('current_project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams_collection.project')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='projects', to='crams_contact.department')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='project_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archive_ts', models.DateTimeField(blank=True, null=True)),
                ('reference', models.CharField(max_length=255)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='publications', to='crams_collection.project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectQuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archive_ts', models.DateTimeField(blank=True, null=True)),
                ('question_response', models.TextField(blank=True, max_length=1024)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='project_question_responses', to='crams_collection.project')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='project_question_responses', to='crams.question')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectProvisionDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='linked_provisiondetails', to='crams_collection.project')),
                ('provision_details', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='linked_projects', to='crams.provisiondetails')),
            ],
        ),
        migrations.CreateModel(
            name='OrganisationContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='crams_contact.contact')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams_contact.department')),
                ('faculty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams_contact.faculty')),
                ('organisation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams_contact.organisation')),
            ],
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archive_ts', models.DateTimeField(blank=True, null=True)),
                ('funding_body_and_scheme', models.CharField(max_length=200)),
                ('grant_id', models.CharField(blank=True, max_length=200, null=True)),
                ('start_year', models.IntegerField(error_messages={'max_value': 'Please input a year between 1970 ~ 3000', 'min_value': 'Please input a year between 1970 ~ 3000'}, validators=[django.core.validators.MinValueValidator(1970), django.core.validators.MaxValueValidator(3000)])),
                ('duration', models.IntegerField(error_messages={'max_value': 'Please enter funding duration (in months 1~1000).', 'min_value': 'Please enter funding duration (in months 1-1000).'}, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)])),
                ('total_funding', models.FloatField(blank=True, default=0.0)),
                ('grant_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='grants', to='crams_collection.granttype')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='grants', to='crams_collection.project')),
            ],
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.FloatField(default=0.0)),
                ('for_code', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='domains', to='crams.forcode')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='domains', to='crams_collection.project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=64)),
                ('parent_erb_project_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams_collection.projectid')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='archive_project_ids', to='crams_collection.project')),
                ('provision_details', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='projectid', to='crams.provisiondetails')),
                ('system', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='project_ids', to='crams.eresearchbodyidkey')),
            ],
            options={
                'index_together': {('identifier', 'project', 'system')},
            },
        ),
        migrations.CreateModel(
            name='ProjectContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='project_contacts', to='crams_contact.contact')),
                ('contact_role', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='project_contacts', to='crams_contact.contactrole')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='project_contacts', to='crams_collection.project')),
            ],
            options={
                'unique_together': {('project', 'contact', 'contact_role')},
                'index_together': {('project', 'contact', 'contact_role')},
            },
        ),
    ]
