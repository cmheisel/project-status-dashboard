# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-16 14:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_fill_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectsummary',
            name='updated_at',
            field=models.DateTimeField(),
        ),
    ]
