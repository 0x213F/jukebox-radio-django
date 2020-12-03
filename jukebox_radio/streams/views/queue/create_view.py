import json

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class QueueCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        TODO
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.select_related("now_playing").get(user=request.user)

        generic_uuid = request.POST.get("uuid")
        class_name = request.POST.get("class")

        track = Track.objects.get(uuid=generic_uuid) if class_name == 'Track' else None
        collection = Collection.objects.get(uuid=generic_uuid) if class_name == 'Collection' else None

        # TODO need to finish up track and collection objects if they are not fully complete

        try:
            prev_queue_ptr = Queue.objects.get(stream=stream, next_queue_ptr=None, played_at__isnull=True, deleted_at__isnull=True)
            is_head = False
        except Queue.DoesNotExist:
            prev_queue_ptr = None
            is_head = True
        next_queue_ptr = None

        is_abstract = bool(collection)
        queue = Queue.objects.create(
            user=request.user,
            track=track,
            collection=collection,
            stream=stream,
            prev_queue_ptr=prev_queue_ptr,
            next_queue_ptr=next_queue_ptr,
            is_abstract=is_abstract,
            parent_queue_ptr=None,
            is_head=is_head,
            is_tail=True,
        )

        if prev_queue_ptr:
            prev_queue_ptr.next_queue_ptr = queue
            prev_queue_ptr.save()

        return self.http_response_200(
            {
                "trackUuid": track.uuid if track else None,
                "collectionUuid": collection.uuid if collection else None,
                "streamId": queue.stream_id,
                "prevQueuePtr": queue.prev_queue_ptr_id,
                "nextQueuePtr": queue.next_queue_ptr_id,
                "isAbstract": queue.is_abstract,
                "parentQueuePtrId": queue.parent_queue_ptr_id,
            }
        )
