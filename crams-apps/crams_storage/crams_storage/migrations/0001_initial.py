# Generated by Django 3.1.1 on 2021-03-08 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crams', '0008_load_crams_lookups'),
    ]

    operations = [
        migrations.CreateModel(
            name='StorageType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storage_type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='StorageProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('unit_cost', models.FloatField(default=0.0)),
                ('operational_cost', models.FloatField(default=0.0)),
                ('capacity', models.FloatField(default=0.0)),
                ('cost_unit_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='storageproduct', to='crams.costunittype')),
                ('e_research_system', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='storageproduct', to='crams.eresearchbodysystem')),
                ('funding_body', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='storageproduct', to='crams.fundingbody')),
                ('parent_storage_product', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crams_storage.storageproduct')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='storageproduct', to='crams.provider')),
                ('storage_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='storage_products', to='crams_storage.storagetype')),
                ('zone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='storage_products', to='crams.zone')),
            ],
            options={
                'unique_together': {('name', 'e_research_system', 'storage_type', 'zone')},
                'index_together': {('name', 'e_research_system')},
            },
        ),
        migrations.CreateModel(
            name='StorageProductProvisionId',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provision_id', models.CharField(blank=True, max_length=255, null=True)),
                ('storage_product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='crams_storage.storageproduct')),
            ],
            options={
                'unique_together': {('provision_id', 'storage_product')},
                'index_together': {('provision_id', 'storage_product')},
            },
        ),
    ]
