from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.database import acquire_manage_queue_intervals_lock


class QueueIntervalCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user wants to play the "up next queue item" right now.
        """
        Queue = apps.get_model("streams", "Queue")

        queue_uuid = self.param(request, "queueUuid")
        with acquire_manage_queue_intervals_lock(queue_uuid):
            queue = self._create_queue_interval(request)

        return self.http_react_response(
            "queue/update",
            {
                "queues": [Queue.objects.serialize(queue)],
            },
        )

    def _create_queue_interval(self, request):
        """
        Create a QueueInterval.
        """
        Marker = apps.get_model("streams", "Marker")
        QueueInterval = apps.get_model("streams", "QueueInterval")
        Queue = apps.get_model("streams", "Queue")

        # Query parameters
        queue_uuid = self.param(request, "queueUuid")
        lower_bound_marker_uuid = self.param(request, "lowerBoundMarkerUuid")
        upper_bound_marker_uuid = self.param(request, "upperBoundMarkerUuid")
        purpose = self.param(request, "purpose")
        stem_vocals = self.param(request, "stemVocals")
        stem_drums = self.param(request, "stemDrums")
        stem_bass = self.param(request, "stemBass")
        stem_piano = self.param(request, "stemPiano")
        stem_other = self.param(request, "stemOther")

        # Create the interval
        QueueInterval.objects.create_queue_interval(
            user=request.user,
            queue_id=queue_uuid,
            lower_bound_id=lower_bound_marker_uuid,
            upper_bound_id=upper_bound_marker_uuid,
            purpose=purpose,
            stem_vocals=stem_vocals,
            stem_drums=stem_drums,
            stem_bass=stem_bass,
            stem_piano=stem_piano,
            stem_other=stem_other,
        )

        # Update the queue duration
        if purpose == QueueInterval.PURPOSE_MUTED:
            queue = (
                Queue.objects.select_related("parent")
                .select_related("track")
                .get(uuid=queue_uuid)
            )

            lower_timestamp_ms = (
                Marker.objects.get(uuid=lower_bound_marker_uuid).timestamp_ms
                if lower_bound_marker_uuid
                else 0
            )
            upper_timestamp_ms = (
                Marker.objects.get(uuid=upper_bound_marker_uuid).timestamp_ms
                if upper_bound_marker_uuid
                else queue.track.duration_ms
            )
            interval_duration_ms = upper_timestamp_ms - lower_timestamp_ms

            queue.duration_ms -= interval_duration_ms
            queue.save()
            if queue.parent:
                # NOTE: This returns the parent queue to the application, which
                #       is expected!
                queue = queue.parent
                queue.duration_ms += interval_duration_ms
                queue.save()

        # Queue object (along with related intervals) will be sent back to the
        # application.
        return queue
