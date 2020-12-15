from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from jukebox_radio.core.base_view import BaseView


class StreamPreviousTrackView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "last played track" right now.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.now_playing_id:
            raise ValueError("Nothing is playing!")

        queue = Queue.objects.select_related(
            "prev_queue_ptr", "prev_queue_ptr__track"
        ).get(stream=stream, is_head=True)

        playing_at = timezone.now() + timedelta(milliseconds=125)

        # NOTE: This is a required but temporary block of logic. This case is
        #       hit when a track stops playing and the next queue item is not
        #       automatically played. That behavior is not expected in the long
        #       run.
        if not stream.is_playing and not stream.is_paused:
            stream.played_at = playing_at
            stream.paused_at = None
            stream.save()
            return self.http_response_200({})

        with transaction.atomic():
            stream.now_playing = queue.prev_queue_ptr.track
            stream.played_at = playing_at
            stream.paused_at = None
            stream.save()

            # Update the current head of the queue
            queue.played_at = None
            queue.is_head = False
            queue.save()

            # Mark the new head of the queue
            queue.prev_queue_ptr.played_at = playing_at
            queue.prev_queue_ptr.is_head = True
            queue.prev_queue_ptr.save()

        return self.http_response_200({})
