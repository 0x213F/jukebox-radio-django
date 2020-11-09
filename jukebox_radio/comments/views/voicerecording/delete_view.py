from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class VoiceRecordingDeleteView(BaseView, LoginRequiredMixin):

    def delete(self, request, **kwargs):
        """
        Delete a VoiceRecording.
        """
        VoiceRecording = apps.get_model('comments', 'VoiceRecording')

        voice_recording_uuid = request.DELETE.get('VoiceRecordingUuid')

        voice_recording = (
            VoiceRecording
            .objects
            .get(uuid=voice_recording_uuid, user=request.user)
        )
        voice_recording.delete()

        return self.http_response_200({
            'uuid': voice_recording_uuid,
        })
