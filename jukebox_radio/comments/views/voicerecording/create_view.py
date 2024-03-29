import json
import os
import tempfile
import uuid

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File
from pydub import AudioSegment

from jukebox_radio.core.base_view import BaseView


class VoiceRecordingCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Create a VoiceRecording.
        """
        VoiceRecording = apps.get_model("comments", "VoiceRecording")
        Stream = apps.get_model("streams", "Stream")

        audio_file = request.FILES.get("audioFile")
        transcript_data = json.loads(request.POST["transcriptData"])
        transcript_final = request.POST["transcriptFinal"]
        voice_recording_timestamp = int(request.POST["voiceRecordingTimestamp"])

        # Transform audio into OGG
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(audio_file.read())

        ext = "ogg"
        filename = f"garbage/{uuid.uuid4()}.{ext}"
        audio_segment = AudioSegment.from_file(f.name, "mp3")
        audio_file = File(audio_segment.export(filename, format=ext))
        duration_ms = audio_segment.duration_seconds * 1000

        f.close()
        os.remove(filename)

        stream = Stream.objects.select_related("now_playing__track").get(
            user=request.user
        )

        timestamp_ms = voice_recording_timestamp - duration_ms

        voice_recording = VoiceRecording.objects.create(
            user=request.user,
            audio=audio_file,
            transcript_data=transcript_data,
            transcript_final=transcript_final,
            duration_ms=duration_ms,
            track=stream.now_playing.track,
            timestamp_ms=timestamp_ms,
        )

        return self.http_react_response(
            "voiceRecording/create",
            {
                "voiceRecording": VoiceRecording.objects.serialize(
                    voice_recording, created=True
                )
            },
        )
