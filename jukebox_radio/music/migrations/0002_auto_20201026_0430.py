# Generated by Django 3.0.10 on 2020-10-26 04:30

from django.db import migrations, models
import music.models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='jr_duration_ms',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='jr_img',
            field=models.ImageField(null=True, upload_to=music.models.upload_to_collections_jr_imgs),
        ),
        migrations.AlterField(
            model_name='collection',
            name='jr_name',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='spotify_img',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='spotify_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='spotify_uri',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='youtube_id',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='youtube_img',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='youtube_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='jr_audio',
            field=models.FileField(null=True, upload_to=music.models.upload_to_tracks_jr_audios),
        ),
        migrations.AlterField(
            model_name='track',
            name='jr_duration_ms',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='jr_img',
            field=models.ImageField(null=True, upload_to=music.models.upload_to_tracks_jr_imgs),
        ),
        migrations.AlterField(
            model_name='track',
            name='jr_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='spotify_duration_ms',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='spotify_img',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='spotify_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='spotify_uri',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='youtube_duration_ms',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='youtube_id',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='youtube_img',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='youtube_name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]