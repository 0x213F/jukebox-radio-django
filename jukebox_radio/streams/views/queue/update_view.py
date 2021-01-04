import re

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class QueueUpdateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        User updating the playback configuration of a queue.
        """
        Queue = apps.get_model("streams", "Queue")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        queueUuid = request.POST.get("queueUuid")
        queue = Queue.objects.get(uuid=queueUuid, stream=stream, user=request.user)

        request_attributes = [
            "startAt",
            "endAt",
            "playWithStemSeparation",
            "playBassStem",
            "playDrumsStem",
            "playVocalsStem",
            "playOtherStem",
        ]

        for request_attribute in request_attributes:
            if request_attribute not in request.POST:
                continue

            # TODO: more cleaning/ validation of request data

            value = request.POST.get(request_attribute)

            # camelCase to snake_case
            model_attribute = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

            setattr(queue, model_attribute, value)

        queue.save()

        return self.http_response_200({})
