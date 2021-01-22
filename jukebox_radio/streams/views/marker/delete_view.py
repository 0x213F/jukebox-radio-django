from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class MarkerDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Delete (archive) a Marker.
        """
        Marker = apps.get_model("streams", "Marker")

        marker_uuid = request.POST.get("markerUuid")
        marker = Marker.objects.get(uuid=marker_uuid)
        marker.archive()

        # needed for React Redux to update the state on the FE
        queue_uuid = request.POST.get("queueUuid")

        return self.http_react_response(
            'marker/delete',
            {
                "marker": Marker.objects.serialize(marker),
                "queueUuid": queue_uuid,
            }
        )
