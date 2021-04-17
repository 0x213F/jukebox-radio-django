from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class MarkerCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Create a Marker.
        """
        Marker = apps.get_model("streams", "Marker")

        name = self.param(request, "name")
        track_uuid = self.param(request, "trackUuid")
        timestamp_ms = self.param(request, "timestampMilliseconds")

        marker = Marker.objects.create(
            user=request.user,
            track_id=track_uuid,
            timestamp_ms=timestamp_ms,
            name=name,
        )

        # needed for React Redux to update the state on the FE
        queue_uuid = self.param(request, "queueUuid")

        return self.http_react_response(
            "marker/create",
            {
                "marker": Marker.objects.serialize(marker),
                "queueUuid": queue_uuid,
            },
        )
