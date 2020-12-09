# Generated by Django 3.1.2 on 2020-12-08 23:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('comments', '0002_voicerecording_track'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pghistory', '0003_auto_20201023_1636'),
        ('music', '0002_auto_20201208_2345'),
    ]

    operations = [
        migrations.AddField(
            model_name='voicerecording',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='textcommentmodification',
            name='text_comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='comments.textcomment'),
        ),
        migrations.AddField(
            model_name='textcommentmodification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='textcommentevent',
            name='pgh_context',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='pghistory.context'),
        ),
        migrations.AddField(
            model_name='textcommentevent',
            name='pgh_obj',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='event', to='comments.textcomment'),
        ),
        migrations.AddField(
            model_name='textcommentevent',
            name='track',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', related_query_name='+', to='music.track'),
        ),
        migrations.AddField(
            model_name='textcommentevent',
            name='user',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', related_query_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='textcomment',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='music.track'),
        ),
        migrations.AddField(
            model_name='textcomment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]