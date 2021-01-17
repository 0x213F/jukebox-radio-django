from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class MarkerListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Create a Marker.
        """
        Marker = apps.get_model("streams", "Marker")

        track_uuid = request.POST.get("trackUuid")

        marker_qs = Marker.objects.filter(
            user=request.user,
            track_id=track_uuid,
            deleted_at__isnull=True,
        )

        markers = []
        for marker in marker_qs:
            markers.append(Marker.objects.serialize(marker))

        return self.http_response_200({
            "markers": markers,
        })
