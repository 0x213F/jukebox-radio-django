from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.music.refresh import refresh_collection_external_data
from jukebox_radio.music.refresh import refresh_track_external_data


class QueueCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user adds something to the queue.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        class_name = request.POST.get("className")
        generic_uuid = request.POST.get("genericUuid")
        index = request.POST.get("index", None)

        stream = Stream.objects.select_related("now_playing").get(user=request.user)

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
            index=index,
            user=request.user,
            track=track,
            collection=collection,
            stream=stream,
        )

        return self.http_response_200()
