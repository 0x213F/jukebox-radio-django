import json

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.music.refresh import refresh_collection_external_data
from jukebox_radio.music.refresh import refresh_track_external_data


def get_and_validate_queue_objs(stream, user, prev_queue_uuid, next_queue_uuid):
    """
    Lookup neighboring queues needed to create a new queue.
    """

    # NOTE: For now, the client isn't sending up next or prev queue UUIDs. So
    #       just lookup the most recent queue and use that as the prev value.
    if not related_queue:
        try:
            try:
                prev_queue_ptr = Queue.objects.in_stream(stream)[-1]
            except IndexError:
                prev_queue_ptr = Queue.objects.get(
                    stream=stream,
                    is_head=True,
                )
        except Queue.DoesNotExist:
            prev_queue_ptr = None

    return prev_queue_ptr, None

    # TODO: Eventually, require that the client sends either next or prev
    #       queue. Use the code below instead and delete the above code.
    # related_queue = Queue.objects.filter(uuid_in=[prev_queue_uuid, next_queue_uuid], stream=stream, user=user).get()
    # if related_queue and related_queue.parent_queue_ptr:
    #     raise ValueError(
    #         "You are trying to attach to a queue that has a parent. Try "
    #         "creating a queue attached to the highest level parent "
    #         "instead (parent_queue_ptr must be None)"
    #     )
    #
    # if prev_queue_uuid:
    #     return related_queue, related_queue.next_queue_ptr
    # if next_queue_uuid:
    #     return related_queue.prev_queue_ptr, related_queue


class QueueCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user adds something to the queue.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        class_name = request.POST.get("class")
        generic_uuid = request.POST.get("musicUuid")
        prev_queue_uuid = request.POST.get("prevQueueUuid", None)
        next_queue_uuid = request.POST.get("nextQueueUuid", None)

        stream = Stream.objects.select_related("now_playing").get(user=request.user)

        next_queue_ptr, prev_queue_ptr = get_and_validate_queue_objs(
            stream, request.user, prev_queue_uuid, next_queue_uuid
        )

        # The client either sent a track or a collection UUID. We use class to
        # determine which table to query.
        track = Track.objects.get(uuid=generic_uuid) if class_name == "Track" else None
        collection = (
            Collection.objects.get(uuid=generic_uuid)
            if class_name == "Collection"
            else None
        )
        is_abstract = bool(collection)

        # Refresh external data from provider APIs
        if track:
            refresh_track_external_data(track, request.user)
        if collection:
            refresh_collection_external_data(collection, request.user)

        # Create the queue
        queue = Queue.objects.create(
            user=request.user,
            track=track,
            collection=collection,
            stream=stream,
            prev_queue_ptr_id=prev_queue_uuid,
            next_queue_ptr_id=next_queue_uuid,
            is_abstract=is_abstract,
            parent_queue_ptr=None,
        )

        # Fix pointers
        if prev_queue_ptr:
            related_queue_qs = Queue.objects.filter(prev_queue_ptr=prev_queue_ptr)
            related_queue_qs.update(prev_queue_ptr=queue)

        if next_queue_ptr:
            related_queue_qs = Queue.objects.filter(next_queue_ptr=next_queue_ptr)
            related_queue_qs.update(next_queue_ptr=queue)

        if collection:

            # Here we add all the required child queues for each collection
            # listing (i.e. track on album, track in playlist, et al.) in the
            # collection
            tracks = collection.filter_tracks()
            for _track in tracks:
                track_queue = Queue.objects.create(
                    user=request.user,
                    track=_track,
                    collection=None,
                    stream=stream,
                    prev_queue_ptr=prev_queue_ptr,
                    next_queue_ptr=None,
                    is_abstract=False,
                    parent_queue_ptr=queue,
                )

                if prev_queue_ptr:
                    prev_queue_ptr.next_queue_ptr = track_queue
                    prev_queue_ptr.save()
                prev_queue_ptr = track_queue

        # TODO: return something meaningful
        return self.http_response_200({})
