# Generated by Django 5.0 on 2023-12-30 15:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_status_created_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ['-created_at'], 'verbose_name': 'Status', 'verbose_name_plural': 'Statuses'},
        ),
        migrations.RenameField(
            model_name='status',
            old_name='description',
            new_name='content',
        ),
    ]
