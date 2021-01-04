# Generated by Django 3.1.2 on 2021-01-03 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_auto_20201228_0705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='textcommentmodification',
            name='style',
            field=models.CharField(choices=[('underline', 'Underline'), ('box', 'Box'), ('circle', 'Circle'), ('highlight', 'Highlight'), ('strike-through', 'Strike-through'), ('crossed-off', 'Crossed-off'), ('bracket', 'Bracket')], max_length=32),
        ),
    ]
