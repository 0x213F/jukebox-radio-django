import os
import tempfile

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File

from pydub import AudioSegment

from jukebox_radio.core.base_view import BaseView


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
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(audio_file.read())

        ext = "ogg"
        filename = f"garbage/{audio_file.name}.{ext}"
        audio_segment = AudioSegment.from_mp3(f.name)
        audio_file = File(audio_segment.export(filename, format=ext))

        f.close()
        os.remove(filename)

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

        return self.http_response_200({})
