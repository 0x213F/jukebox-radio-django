import json
import os
import tempfile
import uuid
from datetime import timedelta

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File

from pydub import AudioSegment

from jukebox_radio.core import time as time_util
from jukebox_radio.core.base_view import BaseView

User = get_user_model()


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

        # Morph audio into OGG
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(audio_file.read())

        ext = "ogg"
        filename = f"garbage/{uuid.uuid4()}.{ext}"
        audio_segment = AudioSegment.from_file(f.name, "mp3")
        audio_file = File(audio_segment.export(filename, format=ext))
        duration_ms = audio_segment.duration_seconds * 1000

        f.close()
        os.remove(filename)

        now = time_util.now()

        stream = Stream.objects.select_related("now_playing").get(user=request.user)

        end_of_the_track = stream.played_at + timedelta(
            milliseconds=stream.now_playing.duration_ms
        )
        track_is_over = stream.now_playing and now > end_of_the_track
        if not stream.now_playing or track_is_over:
            return self.http_response_400("No track is currently playing in the stream")

        timestamp_ms = time_util.ms(now - stream.played_at) - duration_ms

        voice_recording = VoiceRecording.objects.create(
            user=request.user,
            audio=audio_file,
            transcript_data=transcript_data,
            transcript_final=transcript_final,
            duration_ms=duration_ms,
            track=stream.now_playing,
            timestamp_ms=timestamp_ms,
        )

        return self.http_response_200(
            {
                "class": voice_recording.__class__.__name__,
                "uuid": voice_recording.uuid,
                "user": voice_recording.user.username,
                "transcriptData": voice_recording.transcript_data,
                "transcriptFinal": voice_recording.transcript_final,
                "durationMilliseconds": voice_recording.duration_ms,
                "trackUuid": voice_recording.track_id,
                "timestampMilliseconds": voice_recording.timestamp_ms,
            }
        )
