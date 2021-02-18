import os
import pathlib
import tempfile
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File

from pydub import AudioSegment

from jukebox_radio.core.base_view import BaseView
# from jukebox_radio.music.tasks import generate_stems_for_track


FIVE_MINUTES = 60 * 5


class TrackGetFilesView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Create a track from upload.
        """
        Track = apps.get_model("music", "Track")

        track_uuid = request.GET.get("trackUuid")

        track = Track.objects.get(
            uuid=track_uuid,
            user=request.user,
        )

        if settings.APP_ENV == settings.APP_ENV_LOCAL:
            scheme = request.scheme
            host = request.get_host()
            audio_url = f'{scheme}://{host}{track.audio.url}'
            img_url = f'{scheme}://{host}{track.img.url}'
        elif settings.APP_ENV == settings.APP_ENV_PROD:
            import boto3
            from botocore.client import Config

            s3_client = boto3.client(
                's3',
                config=Config(signature_version='s3v4'),
                region_name='us-west-1'
            )
            audio_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': 'jukebox-radio-prod',
                    'Key': f'media/{track.audio.name}',
                },
                ExpiresIn=FIVE_MINUTES,
            )
            img_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': 'jukebox-radio-prod',
                    'Key': f'media/{track.img.name}',
                },
                ExpiresIn=FIVE_MINUTES,
            )

        return self.http_react_response(
            "playback/loadFiles",
            {
                "track": {
                    "uuid": track_uuid,
                    'audioUrl': audio_url,
                    'imageUrl': img_url,
                }
            },
        )
