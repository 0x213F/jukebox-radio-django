import boto3
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
            s3_client = boto3.client('s3')
            audio_response = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': 'django-storage',
                    'Key': track.audio.name,
                },
                ExpiresIn=FIVE_MINUTES,
            )
            img_response = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': 'django-storage',
                    'Key': track.img.name,
                },
                ExpiresIn=FIVE_MINUTES,
            )
            audio_url = audio_response['url']
            img_url = img_response['url']

        return self.http_response_200({
            'audioUrl': audio_url,
            'imageUrl': img_url,
        })
