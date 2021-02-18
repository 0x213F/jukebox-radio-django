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
            audio_url = f'{track.audio.url}, {track.audio.path}'
            img_url = f'{track.img.url}, {track.img.path}'

        return self.http_response_200({
            'audioUrl': audio_url,
            'imageUrl': img_url,
        })
