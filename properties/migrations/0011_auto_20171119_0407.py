# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-19 04:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0010_auto_20171119_0112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='status',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
