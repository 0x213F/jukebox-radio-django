# Generated by Django 3.1.2 on 2020-12-01 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='is_head',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='queue',
            name='is_tail',
            field=models.BooleanField(default=False),
        ),
    ]