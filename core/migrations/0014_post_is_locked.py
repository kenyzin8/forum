# Generated by Django 5.0 on 2023-12-30 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_reply_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_locked',
            field=models.BooleanField(default=False),
        ),
    ]
