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
            raise ValueError('The external track data must always be refreshed')

        if class_name == 'Track':
            obj = Track.objects.get(uuid=generic_uuid)
            refresh_track_external_data(obj, request.user)
        elif class_name == 'Collection':
            obj = Collection.objects.get(uuid=generic_uuid)
            refresh_collection_external_data(obj, request.user)
        else:
            raise ValueError(f'Invalid class {class_name}')


            # TODO refresh data inside track or collection. meaning, do a hard
            # refresh on all the data for the track given the external_id. if
            # collection, check/ update/ create the tracks too!
            # TODO Call this before the "add to queue" endpoint on the fe
            # TODO (impliment/ use) doubly linked list sort
            # TODO remove rewind
            # TODO impliment (play/ pause) - play just plays the next queued item

        return self.http_response_200({})