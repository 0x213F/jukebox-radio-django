# Generated by Django 3.1.2 on 2020-11-30 06:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('music', '0001_initial'),
        ('pghistory', '0003_auto_20201023_1636'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('played_at', models.DateTimeField(blank=True, null=True)),
                ('is_playing', models.BooleanField(default=False)),
                ('recording_started_at', models.DateTimeField(blank=True, null=True)),
                ('recording_ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('now_playing', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='music.track')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StreamEvent',
            fields=[
                ('pgh_id', models.AutoField(primary_key=True, serialize=False)),
                ('pgh_created_at', models.DateTimeField(auto_now_add=True)),
                ('pgh_label', models.TextField(help_text='The event label.')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, serialize=False)),
                ('played_at', models.DateTimeField(blank=True, null=True)),
                ('is_playing', models.BooleanField(default=False)),
                ('recording_started_at', models.DateTimeField(blank=True, null=True)),
                ('recording_ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('now_playing', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', related_query_name='+', to='music.track')),
                ('pgh_context', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='pghistory.context')),
                ('pgh_obj', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='event', to='streams.stream')),
                ('user', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', related_query_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_abstract', models.BooleanField()),
                ('played_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('collection', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='music.collection')),
                ('next_queue_ptr', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='streams.queue')),
                ('parent_queue_ptr', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='streams.queue')),
                ('prev_queue_ptr', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='streams.queue')),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='streams.stream')),
                ('track', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='music.track')),
            ],
        ),
    ]
