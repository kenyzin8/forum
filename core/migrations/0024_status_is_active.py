# Generated by Django 5.0 on 2023-12-30 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_remove_status_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
