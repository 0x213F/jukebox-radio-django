from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class VoiceRecordingGetView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        List VoiceRecording objects that the user has created for a given
        track.
        """
        VoiceRecording = apps.get_model("comments", "VoiceRecording")

        voice_recording_uuid = request.GET.get("voiceRecordingUuid")

        voice_recording = VoiceRecording.objects.get(uuid=voice_recording_uuid)

        return self.http_response_200({
            'uuid': voice_recording.uuid,
            'url': voice_recording.audio.url,
        })
