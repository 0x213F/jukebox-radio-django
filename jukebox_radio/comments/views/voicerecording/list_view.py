from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class VoiceRecordingListView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        List VoiceRecording objects that the user has created for a given
        track.
        """
        VoiceRecording = apps.get_model("comments", "VoiceRecording")
        Stream = apps.get_model("streams", "Stream")

        stream = Stream.objects.get(user=request.user)

        if not stream.is_playing and not stream.is_paused:
            return self.http_react_response(
                "voiceRecording/listSet",
                {
                    "voiceRecordings": [],
                },
            )

        track_uuid = stream.now_playing.track_id

        voice_recording_qs = VoiceRecording.objects.context_filter(
            track_uuid, request.user
        )

        voice_recordings = []
        for voice_recording in voice_recording_qs:
            voice_recordings.append(VoiceRecording.objects.serialize(voice_recording))

        return self.http_react_response(
            "voiceRecording/listSet",
            {
                "voiceRecordings": voice_recordings,
            },
        )
