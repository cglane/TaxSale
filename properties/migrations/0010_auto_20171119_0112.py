# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-19 01:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0009_auto_20171118_2356'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='property',
            options={'verbose_name_plural': 'properties'},
        ),
    ]
