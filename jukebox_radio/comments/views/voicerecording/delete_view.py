from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class VoiceRecordingDeleteView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Delete a VoiceRecording.
        """
        VoiceRecording = apps.get_model("comments", "VoiceRecording")

        voice_recording_uuid = request.POST["voiceRecordingUuid"]
        voice_recording = VoiceRecording.objects.get(
            uuid=voice_recording_uuid, user=request.user
        )
        voice_recording.archive()

        return self.http_react_response(
            "voiceRecording/delete",
            {"voiceRecordingUuid": voice_recording_uuid, "trackUuid": voice_recording.track_id },
        )
