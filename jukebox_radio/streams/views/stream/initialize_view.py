from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class StreamInitializeView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        When a user initializes a stream (right after login).
        """
        Stream = apps.get_model("streams", "Stream")

        stream, created = Stream.objects.get_or_create(user=request.user)

        if not created:
            return self.http_response_200()

        Queue.objects.create(
            stream=stream, user=request.user, index=Queue.INITIAL_INDEX, is_head=True, is_abstract=False
        )

        return self.http_response_200()
