from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class VoiceRecordingListView(BaseView, LoginRequiredMixin):

    @csrf_exempt
    def get(self, request, **kwargs):
        """
        List VoiceRecording objects that the user has created for a given
        track.
        """
        VoiceRecording = apps.get_model("comments", "VoiceRecording")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        track_uuid = stream.now_playing_id

        voice_recording_qs = (
            VoiceRecording.objects.select_related("user", "track")
            .filter(track__uuid=track_uuid, user=request.user, deleted_at__isnull=True)
            .order_by("timestamp_ms")
        )
        voice_recordings = []
        for voice_recording in voice_recording_qs:
            voice_recordings.append(
                {
                    "class": voice_recording.__class__.__name__,
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
