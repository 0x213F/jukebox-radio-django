from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


def validate_music_content(track_id, collection_id):
    """
    XOR
    """
    if not bool(track_id) ^ bool(collection_id):
        raise Exception('Must provide "trackId" XOR "collectionId"')


def validate_queue_ptrs(user, prev_queue_ptr_id, next_queue_ptr_id):
    """
    TODO
    """
    Queue = apps.get_model("streams", "Queue")

    stream = Stream.objects.select_related("now_playing").get(user=user)

    if not prev_queue_ptr_id and not next_queue_ptr_id:
        if Queue.objects.filter(stream).exists():
            raise Exception("TODO")


class QueueCreateView(BaseView, LoginRequiredMixin):
    def put(self, request, **kwargs):
        """
        TODO
        """
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.select_related("now_playing").get(user=request.user)

        track_id = request.PUT.get("trackId", None)
        collection_id = request.PUT.get("collectionId", None)
        prev_queue_ptr_id = request.PUT.get("prevQueuePtrId", None)
        next_queue_ptr_id = request.PUT.get("nextQueuePtrId", None)

        try:
            validate_music_content(track_id, collection_id)
        except Exception as msg:
            return http_response_400(msg)

        try:
            validate_queue_ptrs(request.user, prev_queue_ptr_id, next_queue_ptr_id)
        except Exception as msg:
            return http_response_400(msg)

        is_abstract = bool(collection_id)
        queue = Queue.objects.create(
            track_id=track_id,
            collection_id=collection_id,
            stream=stream,
            prev_queue_ptr_id=prev_queue_ptr_id,
            next_queue_ptr_id=next_queue_ptr_id,
            is_abstract=is_abstract,
            parent_queue_ptr=None,
        )

        return self.http_response_200(
            {
                "trackId": queue.track_id,
                "collectionId": queue.collection_id,
                "streamId": queue.stream_id,
                "prevQueuePtr": queue.prev_queue_ptr_id,
                "nextQueuePtr": queue.next_queue_ptr_id,
                "isAbstract": queue.is_abstract,
                "parentQueuePtrId": queue.parent_queue_ptr_id,
            }
        )
