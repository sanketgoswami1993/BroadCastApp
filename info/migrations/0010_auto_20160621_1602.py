# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-21 10:32
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0009_auto_20160613_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordconfirm',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 22, 16, 2, 2, 154000)),
        ),
    ]
