# Generated by Django 2.0 on 2020-07-08 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('meetup', '0001_initial'),
        ('users', '0001_initial'),
        ('cities_light', '0006_compensate_for_0003_bytestring_bug'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportrequest',
            name='volunteer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.SystersUser', verbose_name='Volunteer'),
        ),
        migrations.AddField(
            model_name='rsvp',
            name='meetup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meetup.Meetup', verbose_name='Meetup'),
        ),
        migrations.AddField(
            model_name='rsvp',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.SystersUser', verbose_name='User'),
        ),
        migrations.AddField(
            model_name='requestmeetup',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approvedBy', to='users.SystersUser'),
        ),
        migrations.AddField(
            model_name='requestmeetup',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.SystersUser', verbose_name='Created By'),
        ),
        migrations.AddField(
            model_name='requestmeetup',
            name='meetup_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cities_light.City', verbose_name='Meetup Location'),
        ),
        migrations.AddField(
            model_name='meetup',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.SystersUser', verbose_name='Created By'),
        ),
        migrations.AddField(
            model_name='meetup',
            name='leader',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='community_leader', to='users.SystersUser', verbose_name='Community leader'),
        ),
        migrations.AddField(
            model_name='meetup',
            name='meetup_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cities_light.City', verbose_name='Meetup Location'),
        ),
        migrations.AlterUniqueTogether(
            name='rsvp',
            unique_together={('user', 'meetup')},
        ),
    ]
