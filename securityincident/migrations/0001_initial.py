# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AfgIncidentOasis',
            fields=[
                ('uid', models.IntegerField(serialize=False, primary_key=True, db_column=b'UID')),
                ('xmin', models.FloatField(null=True, db_column=b'XMIN', blank=True)),
                ('xmax', models.FloatField(null=True, db_column=b'XMAX', blank=True)),
                ('ymin', models.FloatField(null=True, db_column=b'YMIN', blank=True)),
                ('ymax', models.FloatField(null=True, db_column=b'YMAX', blank=True)),
                ('id', models.CharField(max_length=255, db_column=b'ID', blank=True)),
                ('name', models.CharField(max_length=255, db_column=b'NAME', blank=True)),
                ('type', models.CharField(max_length=255, db_column=b'TYPE', blank=True)),
                ('target', models.CharField(max_length=255, db_column=b'TARGET', blank=True)),
                ('dead', models.IntegerField(null=True, blank=True)),
                ('affected', models.IntegerField(null=True, blank=True)),
                ('violent', models.IntegerField(null=True, blank=True)),
                ('injured', models.IntegerField(null=True, blank=True)),
                ('incident_date', models.DateField(null=True, blank=True)),
                ('time00', models.CharField(max_length=255, blank=True)),
                ('locdesc', models.CharField(max_length=255, blank=True)),
                ('source', models.CharField(max_length=255, blank=True)),
                ('town', models.CharField(max_length=255, blank=True)),
                ('district', models.CharField(max_length=255, blank=True)),
                ('province', models.CharField(max_length=255, blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('scoring', models.IntegerField(null=True, blank=True)),
                ('incident_dateserial', models.BigIntegerField(null=True, blank=True)),
                ('wkb_geometry', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('accumulative_affected', models.IntegerField(null=True, blank=True)),
                ('main_type', models.CharField(max_length=255, blank=True)),
                ('main_target', models.CharField(max_length=255, blank=True)),
                ('prov_code', models.IntegerField(null=True, blank=True)),
                ('dist_code', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'afg_incident_oasis',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AfgIncidentOasisTemp',
            fields=[
                ('uid', models.IntegerField(serialize=False, primary_key=True, db_column=b'UID')),
                ('name', models.CharField(max_length=255, db_column=b'NAME', blank=True)),
                ('type', models.CharField(max_length=255, db_column=b'TYPE', blank=True)),
                ('target', models.CharField(max_length=255, db_column=b'TARGET', blank=True)),
                ('dead', models.IntegerField(null=True, blank=True)),
                ('affected', models.IntegerField(null=True, blank=True)),
                ('violent', models.IntegerField(null=True, blank=True)),
                ('injured', models.IntegerField(null=True, blank=True)),
                ('incident_date', models.DateField(null=True, blank=True)),
                ('locdesc', models.CharField(max_length=255, blank=True)),
                ('source', models.CharField(max_length=255, blank=True)),
                ('town', models.CharField(max_length=255, blank=True)),
                ('district', models.CharField(max_length=255, blank=True)),
                ('province', models.CharField(max_length=255, blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('wkb_geometry', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
            ],
            options={
                'db_table': 'afg_incident_oasis_temp',
                'managed': True,
            },
        ),
    ]
