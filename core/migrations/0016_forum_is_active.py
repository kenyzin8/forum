# Generated by Django 5.0 on 2023-12-30 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_forum_node_forum'),
    ]

    operations = [
        migrations.AddField(
            model_name='forum',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
