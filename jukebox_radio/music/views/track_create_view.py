import os
import pathlib
import tempfile
import uuid

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File
from pydub import AudioSegment

from jukebox_radio.core.base_view import BaseView


class TrackCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Create a track from upload.
        """
        Track = apps.get_model("music", "Track")

        track_name = request.POST.get("trackName")
        artist_name = request.POST.get("artistName")
        album_name = request.POST.get("albumName")

        audio_file = request.FILES.get("audioFile")
        image_file = request.FILES.get("imageFile")

        # Morph audio into OGG
        try:
            upload_file_ext = pathlib.Path(audio_file.temporary_file_path()).suffix[1:]
        except Exception:
            upload_file_ext = "m4a"
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(audio_file.read())

        ext = "ogg"
        temp_filename = f"./garbage/{uuid.uuid4()}.{ext}"
        audio_segment = AudioSegment.from_file(f.name, upload_file_ext)
        audio_file = File(audio_segment.export(temp_filename, format=ext))

        f.close()
        os.remove(temp_filename)

        Track.objects.create(
            user=request.user,
            format=Track.FORMAT_TRACK,
            provider=Track.PROVIDER_JUKEBOX_RADIO,
            name=track_name,
            artist_name=artist_name,
            album_name=album_name,
            audio=audio_file,
            img=image_file,
            duration_ms=audio_segment.duration_seconds * 1000,
        )

        return self.http_response_200({})
