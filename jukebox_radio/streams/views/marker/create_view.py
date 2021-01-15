from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class MarkerCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Create a Marker.
        """
        Marker = apps.get_model("streams", "Marker")

        track_uuid = request.POST.get("trackUuid")
        timestamp_ms = request.POST.get("timestampMilliseconds")

        marker = Marker.objects.create(
            user=request.user,
            track_id=track_uuid,
            timestamp_ms=timestamp_ms,
        )

        return self.http_response_200()
