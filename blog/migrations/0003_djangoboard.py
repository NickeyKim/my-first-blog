# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='DjangoBoard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('subject', models.CharField(max_length=50, blank=True)),
                ('name', models.CharField(max_length=50, blank=True)),
                ('created_date', models.DateField(null=True, blank=True)),
                ('mail', models.CharField(max_length=50, blank=True)),
                ('memo', models.CharField(max_length=200, blank=True)),
                ('hits', models.IntegerField(null=True, blank=True)),
            ],
        ),
    ]
