# Generated by Django 3.2.4 on 2021-08-23 02:26

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crams_storage', '0002_init_lookups'),
        ('crams_contact', '0003_contactlog'),
        ('crams_compute', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crams_collection', '0004_projectlog'),
        ('crams', '0010_projectmemberstatus_lookups'),
        ('crams_log', '0002_userlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllocationHome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ComputeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instances', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('approved_instances', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('cores', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('approved_cores', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('core_hours', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('approved_core_hours', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('compute_product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='compute_requests', to='crams_compute.computeproduct')),
                ('provision_details', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='computerequest', to='crams.provisiondetails')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('data_sensitive', models.BooleanField(blank=True, null=True)),
                ('national_percent', models.PositiveSmallIntegerField(default=100, validators=[django.core.validators.MaxValueValidator(100)])),
                ('transaction_id', models.CharField(blank=True, max_length=99, null=True)),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField()),
                ('approval_notes', models.TextField(blank=True, max_length=1024, null=True)),
                ('sent_email', models.BooleanField(default=True)),
                ('allocation_extension_count', models.PositiveSmallIntegerField(default=0)),
                ('sent_ext_support_email', models.BooleanField(default=False)),
                ('allocation_home', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='requests', to='crams_allocation.allocationhome')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='request_created_by', to=settings.AUTH_USER_MODEL)),
                ('current_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='history', to='crams_allocation.request')),
                ('e_research_system', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='eresearch_systems', to='crams.eresearchbodysystem')),
                ('funding_scheme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='requests', to='crams.fundingscheme')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='requests', to='crams_collection.project')),
            ],
        ),
        migrations.CreateModel(
            name='RequestStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=100)),
                ('transient', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='StorageRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_quota', models.FloatField(default=0.0)),
                ('requested_quota_change', models.FloatField(default=0.0)),
                ('approved_quota_change', models.FloatField(default=0.0)),
                ('provision_details', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='storagerequest', to='crams.provisiondetails')),
                ('provision_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='storage_requests', to='crams_storage.storageproductprovisionid')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='storage_requests', to='crams_allocation.request')),
                ('storage_product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='storage_requests', to='crams_storage.storageproduct')),
            ],
        ),
        migrations.CreateModel(
            name='StorageRequestQuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archive_ts', models.DateTimeField(blank=True, null=True)),
                ('question_response', models.TextField(blank=True, max_length=1024)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='storage_question_responses', to='crams.question')),
                ('storage_allocation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='storage_question_responses', to='crams_allocation.storagerequest')),
            ],
        ),
        migrations.CreateModel(
            name='RequestQuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archive_ts', models.DateTimeField(blank=True, null=True)),
                ('question_response', models.TextField(blank=True, max_length=1024)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='request_question_responses', to='crams.question')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='request_question_responses', to='crams_allocation.request')),
            ],
        ),
        migrations.AddField(
            model_name='request',
            name='request_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='requests', to='crams_allocation.requeststatus'),
        ),
        migrations.AddField(
            model_name='request',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='request_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_file_path', models.CharField(max_length=99)),
                ('alert_funding_body', models.BooleanField(default=False)),
                ('e_research_body', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams.eresearchbody')),
                ('e_research_system', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='notification_templates', to='crams.eresearchbodysystem')),
                ('funding_body', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='notification_templates', to='crams.fundingbody')),
                ('project_member_status', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams.projectmemberstatus')),
                ('request_status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams_allocation.requeststatus')),
                ('system_key', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams.eresearchbodyidkey')),
            ],
            options={
                'unique_together': {('e_research_system', 'request_status', 'system_key', 'template_file_path')},
                'index_together': {('request_status', 'e_research_system', 'template_file_path')},
            },
        ),
        migrations.CreateModel(
            name='ERBRequestStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('extension_count_data_point', models.SmallIntegerField(default=1)),
                ('display_name', models.CharField(max_length=99)),
                ('e_research_body', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams.eresearchbody')),
                ('e_research_system', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams.eresearchbodysystem')),
                ('request_status', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='erb_status_names', to='crams_allocation.requeststatus')),
            ],
        ),
        migrations.CreateModel(
            name='ComputeRequestQuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archive_ts', models.DateTimeField(blank=True, null=True)),
                ('question_response', models.TextField(blank=True, max_length=1024)),
                ('compute_request', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='compute_question_responses', to='crams_allocation.computerequest')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='compute_question_responses', to='crams.question')),
            ],
        ),
        migrations.AddField(
            model_name='computerequest',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='compute_requests', to='crams_allocation.request'),
        ),
        migrations.CreateModel(
            name='NotificationContactRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_role', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='notifications', to='crams_contact.contactrole')),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='notify_roles', to='crams_allocation.notificationtemplate')),
            ],
            options={
                'index_together': {('notification', 'contact_role')},
            },
        ),
        migrations.CreateModel(
            name='AllocationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crams_request_db_id', models.IntegerField()),
                ('crams_project_db_id', models.IntegerField(blank=True, null=True)),
                ('log_parent', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='allocationlog', to='crams_log.cramslog')),
            ],
            options={
                'unique_together': {('crams_request_db_id', 'log_parent')},
            },
        ),
    ]
