# Generated by Django 3.0.10 on 2020-10-26 03:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('music', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('played_at', models.DateTimeField()),
                ('is_playing', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('now_playing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='music.Track')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_abstract', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField()),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='music.Collection')),
                ('next_queue_ptr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='streams.Queue')),
                ('parent_queue_ptr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='streams.Queue')),
                ('prev_queue_ptr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='streams.Queue')),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='streams.Stream')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='music.Track')),
            ],
        ),
    ]
