# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-05 07:06
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0005_passwordconfirm'),
    ]

    operations = [
        migrations.AddField(
            model_name='passwordconfirm',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 6, 12, 36, 38, 621000)),
        ),
    ]
