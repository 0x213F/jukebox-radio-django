# Generated by Django 3.1.2 on 2021-01-21 01:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0006_auto_20210117_2146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='queueinterval',
            name='repeat_count',
        ),
    ]
