import tempfile

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

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

        print(request.POST)
        print(track_name)

        audio_file = request.FILES.get("audio_file")
        img_file = request.FILES.get("img_file")

        # with tempfile.TemporaryFile() as f:
        #     data = audio_file.read()
        #     f.write(data)

        track = Track.objects.create(
            user=request.user,
            format=Track.FORMAT_TRACK,
            provider=Track.PROVIDER_JUKEBOX_RADIO,
            name=track_name,
            artist_name=artist_name,
            album_name=album_name,
            audio=audio_file,
            img=img_file,
        )

        return self.http_response_200({})
