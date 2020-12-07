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
        Given a query, get relevant collections.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")

        generic_uuid = request.POST.get("musicUuid")
        class_name = request.POST.get("class")
        refresh_data = request.POST.get("refreshData")

        if not refresh_data:
            raise ValueError("The external track data must always be refreshed")

        if class_name == "Track":
            obj = Track.objects.get(uuid=generic_uuid)
            refresh_track_external_data(obj, request.user)
        elif class_name == "Collection":
            obj = Collection.objects.get(uuid=generic_uuid)
            refresh_collection_external_data(obj, request.user)
        else:
            raise ValueError(f"Invalid class {class_name}")

            # TODO refresh spotify album and playlist
            # TODO impliment (play/ pause) - play just plays the next queued item
            #      note this doesn't actually play the item on the front-end,
            #      just does it on the back-end.
            # TODO impliment (seek forward/ seek backward)
            # TODO impliment (next/ previous/ rewind)
            # TODO use this endpoint before creating a queue with a partial track

        return self.http_response_200({})
