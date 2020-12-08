import json

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.music.refresh import refresh_collection_external_data
from jukebox_radio.music.refresh import refresh_track_external_data

User = get_user_model()


class QueueCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Add to queue.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.select_related("now_playing").get(user=request.user)

        generic_uuid = request.POST.get("musicUuid")
        class_name = request.POST.get("class")

        track = Track.objects.get(uuid=generic_uuid) if class_name == "Track" else None
        collection = (
            Collection.objects.get(uuid=generic_uuid)
            if class_name == "Collection"
            else None
        )

        if track:
            refresh_track_external_data(track, request.user)
        if collection:
            refresh_collection_external_data(collection, request.user)

        try:
            prev_queue_ptr = Queue.objects.get(
                stream=stream,
                next_queue_ptr=None,
                played_at__isnull=True,
                deleted_at__isnull=True,
            )
        except Queue.DoesNotExist:
            prev_queue_ptr = None

        is_abstract = bool(collection)
        queue = Queue.objects.create(
            user=request.user,
            track=track,
            collection=collection,
            stream=stream,
            prev_queue_ptr=prev_queue_ptr,
            next_queue_ptr=None,
            is_abstract=is_abstract,
            parent_queue_ptr=None,
        )

        if prev_queue_ptr:
            prev_queue_ptr.next_queue_ptr = queue
            prev_queue_ptr.save()

        if collection:
            next_queue_ptr = None
            last_queue = None
            tracks = collection.filter_tracks()
            for _track in tracks:
                temp_queue = Queue.objects.create(
                    user=request.user,
                    track=_track,
                    collection=None,
                    stream=stream,
                    prev_queue_ptr=prev_queue_ptr,
                    next_queue_ptr=None,
                    is_abstract=False,
                    parent_queue_ptr=queue,
                )

                prev_queue_ptr = queue
                if last_queue:
                    last_queue.next_queue_ptr = queue
                    last_queue.save()

                last_queue = temp_queue


        return self.http_response_200({})
