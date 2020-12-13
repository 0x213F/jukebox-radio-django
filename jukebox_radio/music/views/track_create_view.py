import os
import pathlib
import tempfile
import uuid

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File
from django.conf import settings

from pydub import AudioSegment
from spleeter.separator import Separator

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.music.tasks import generate_stems_for_track


class TrackCreateView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Given a query, get relevant collections.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")

        track_name = request.POST.get("track_name")
        artist_name = request.POST.get("artist_name")
        album_name = request.POST.get("album_name")

        audio_file = request.FILES.get("audio_file")
        img_file = request.FILES.get("img_file")

        # Morph audio into OGG
        upload_file_ext = pathlib.Path(audio_file.temporary_file_path()).suffix[1:]
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(audio_file.read())

        ext = "ogg"
        temp_filename = f"./garbage/{uuid.uuid4()}.{ext}"
        audio_segment = AudioSegment.from_file(f.name, upload_file_ext)
        audio_file = File(audio_segment.export(temp_filename, format=ext))

        f.close()
        os.remove(temp_filename)

        track = Track.objects.create(
            user=request.user,
            format=Track.FORMAT_TRACK,
            provider=Track.PROVIDER_JUKEBOX_RADIO,
            name=track_name,
            artist_name=artist_name,
            album_name=album_name,
            audio=audio_file,
            img=img_file,
            duration_ms=audio_segment.duration_seconds * 1000,
        )

        generate_stems_for_track.delay(track.uuid)

        return self.http_response_200({})
