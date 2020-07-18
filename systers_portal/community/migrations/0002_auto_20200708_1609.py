# Generated by Django 2.0 on 2020-07-08 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('community', '0001_initial'),
        ('cities_light', '0006_compensate_for_0003_bytestring_bug'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestcommunity',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.SystersUser', verbose_name='Approved by'),
        ),
        migrations.AddField(
            model_name='requestcommunity',
            name='location',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='cities_light.City', verbose_name='Location'),
        ),
        migrations.AddField(
            model_name='requestcommunity',
            name='parent_community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='community.Community', verbose_name='Parent community'),
        ),
        migrations.AddField(
            model_name='requestcommunity',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requestor', to='users.SystersUser', verbose_name='Created by'),
        ),
        migrations.AddField(
            model_name='communitypage',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.SystersUser', verbose_name='Author'),
        ),
        migrations.AddField(
            model_name='communitypage',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.Community', verbose_name='Community'),
        ),
        migrations.AddField(
            model_name='community',
            name='admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community', to='users.SystersUser', verbose_name='Community admin'),
        ),
        migrations.AddField(
            model_name='community',
            name='location',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='cities_light.City', verbose_name='Location'),
        ),
        migrations.AddField(
            model_name='community',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='communities', to='users.SystersUser', verbose_name='Members'),
        ),
        migrations.AddField(
            model_name='community',
            name='parent_community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='community.Community', verbose_name='Parent community'),
        ),
        migrations.AlterUniqueTogether(
            name='communitypage',
            unique_together={('community', 'order'), ('community', 'slug')},
        ),
    ]