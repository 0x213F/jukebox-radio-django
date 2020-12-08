import os
import tempfile

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File

from pydub import AudioSegment

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.music.refresh import refresh_collection_external_data
from jukebox_radio.music.refresh import refresh_track_external_data


class TrackUpdateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        TODO
        """
        return self.http_response_200({})
