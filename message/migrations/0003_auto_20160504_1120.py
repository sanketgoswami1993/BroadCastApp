# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-04 05:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0002_auto_20160503_1415'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='attachment',
        ),
        migrations.AddField(
            model_name='attachment',
            name='message',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='message_attachment_rel', to='message.Message'),
            preserve_default=False,
        ),
    ]
