from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class VoiceRecordingCreateView(BaseView, LoginRequiredMixin):
    def put(self, request, **kwargs):
        """
        Create a VoiceRecording.
        """
        VoiceRecording = apps.get_model("comments", "VoiceRecording")

        audio = request.FILES["audio"]
        duration_ms = request.PUT["duration_ms"]
        transcript_data = request.PUT["transcriptData"]
        transcript_final = request.PUT["transcriptFinal"]

        now = time_util.now()
        stream = Stream.objects.select_related("now_playing").get(user=request.user)

        timestamp_ms = time_util.ms(now - stream.played_at) - duration_ms

        voice_recording = VoiceRecording.objects.create(
            user=request.user,
            audio=audio,
            transcript_data=transcript_data,
            transcript_final=transcript_final,
            duration_ms=duration_ms,
            track=stream.now_playing,
            timestamp_ms=timestamp_ms,
        )

        return self.http_response_200(
            {
                "uuid": voice_recording.uuid,
                "user": voice_recording.user.username,
                "transcriptData": voice_recording.transcript_data,
                "transcriptFinal": voice_recording.transcript_final,
                "durationMilliseconds": voice_recording.duration_ms,
                "trackId": voice_recording.track_id,
                "timestampMilliseconds": voice_recording.timestamp_ms,
            }
        )
