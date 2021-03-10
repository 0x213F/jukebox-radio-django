from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_modify_queue_lock
from jukebox_radio.music.refresh import (
    refresh_collection_external_data,
    refresh_track_external_data,
)


class QueueCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)
        with self.acquire_modify_queue_lock(stream):
            self._create_queue(request, stream)

        return self.http_response_200()

    def _create_queue(self, request, stream):
        """
        When a user adds something to the queue.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")

        class_name = self.param(request, "className")
        generic_uuid = self.param(request, "genericUuid")

        # The client either sent a track or a collection UUID. We use class to
        # determine which table to query.
        track = Track.objects.get(uuid=generic_uuid) if class_name == "Track" else None
        collection = (
            Collection.objects.get(uuid=generic_uuid)
            if class_name == "Collection"
            else None
        )

        # Refresh external data from provider APIs
        if track:
            refresh_track_external_data(track, request.user)
        if collection:
            refresh_collection_external_data(collection, request.user)

        Queue.objects.create_queue(
            user=request.user,
            track=track,
            collection=collection,
            stream=stream,
        )
