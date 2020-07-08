# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_squashed_0003_auto_20160207_1550'),
        ('community', '0003_auto_20140928_2034'),
    ]

    operations = [
        migrations.CreateModel(
            name='JoinRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(related_name=b'approved_by', blank=True, to='users.SystersUser', null=True, on_delete=models.CASCADE)),
                ('community', models.ForeignKey(to='community.Community', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(related_name=b'created_by', to='users.SystersUser', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
