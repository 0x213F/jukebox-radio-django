# Generated by Django 3.1.2 on 2021-07-03 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0006_auto_20210703_0531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queueinterval',
            name='purpose',
            field=models.CharField(choices=[('muted', 'Muted'), ('stem_isolation', 'Stem Isolation')], max_length=32),
        ),
    ]