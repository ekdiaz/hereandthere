# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-30 02:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distance', '0008_message_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(default='Chicago', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(default='United States of America', max_length=100),
        ),
    ]