# Generated by Django 3.1.2 on 2021-01-17 21:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0004_queueinterval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queueinterval',
            name='queue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='intervals', to='streams.queue'),
        ),
    ]