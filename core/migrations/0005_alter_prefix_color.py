# Generated by Django 5.0 on 2023-12-29 03:22

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_prefix_post_prefix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prefix',
            name='color',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None),
        ),
    ]
