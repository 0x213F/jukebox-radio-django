from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class VoiceRecordingListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        List VoiceRecording objects that the user has created for a given
        track.
        """
        VoiceRecording = apps.get_model("comments", "VoiceRecording")

        track_uuid = request.GET.get("trackUuid")

        voice_recording_qs = (
            VoiceRecording.objects.select_related("user", "track")
            .filter(track__uuid=track_uuid, user=request.user)
            .order_by("timestamp_ms")
        )
        voice_recordings = []
        for voice_recording in voice_recording_qs:
            voice_recordings.append(
                {
                    "uuid": voice_recording.uuid,
                    "user": voice_recording.user.username,
                    "transcriptData": voice_recording.transcript_data,
                    "transcriptFinal": voice_recording.transcript_final,
                    "durationMilliseconds": voice_recording.duration_ms,
                    "trackUuid": voice_recording.track.uuid,
                    "timestampMilliseconds": voice_recording.timestamp_ms,
                }
            )

        return self.http_response_200(voice_recordings)
