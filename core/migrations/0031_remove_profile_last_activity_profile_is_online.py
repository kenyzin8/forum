# Generated by Django 5.0 on 2023-12-31 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_profile_last_activity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='last_activity',
        ),
        migrations.AddField(
            model_name='profile',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
    ]
