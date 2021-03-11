from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class MarkerListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        List Markers.
        """
        Marker = apps.get_model("streams", "Marker")

        track_uuid = request.GET.get("trackUuid")

        marker_qs = Marker.objects.filter_by_track_and_user(track_uuid, request.user)

        markers = []
        for marker in marker_qs:
            markers.append(Marker.objects.serialize(marker))

        # needed for React Redux to update the state on the FE
        queue_uuid = request.GET.get("queueUuid")

        return self.http_react_response(
            "marker/list",
            {
                "markers": markers,
                "queueUuid": queue_uuid,
            },
        )
