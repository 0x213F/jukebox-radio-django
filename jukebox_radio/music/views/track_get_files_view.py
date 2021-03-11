from django.apps import apps
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.utils import generate_presigned_url

# from jukebox_radio.music.tasks import generate_stems_for_track


class TrackGetFilesView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Create a track from upload.
        """
        Track = apps.get_model("music", "Track")
        Stem = apps.get_model("music", "Stem")

        track_uuid = request.GET.get("trackUuid")

        track = Track.objects.get(
            uuid=track_uuid,
            user=request.user,
        )
        stems = Stem.objects.filter(track_id=track.uuid)

        stems_list = []
        if settings.APP_ENV == settings.APP_ENV_LOCAL:
            scheme = request.scheme
            host = request.get_host()
            audio_url = f"{scheme}://{host}{track.audio.url}"
            img_url = f"{scheme}://{host}{track.img.url}"

            for stem in stems:
                stem_url = f"{scheme}://{host}{stem.audio.url}"
                stems_list.append(
                    {
                        "uuid": stem.uuid,
                        "instrument": stem.instrument,
                        "audioUrl": stem_url,
                    }
                )

        elif settings.APP_ENV == settings.APP_ENV_PROD:
            audio_url = generate_presigned_url(track.audio)
            img_url = generate_presigned_url(track.img)

            for stem in stems:
                stem_url = generate_presigned_url(stem.audio)
                stems_list.append(
                    {
                        "uuid": stem.uuid,
                        "instrument": stem.instrument,
                        "audioUrl": stem_url,
                    }
                )

        return self.http_react_response(
            "playback/loadFiles",
            {
                "track": {
                    "uuid": track_uuid,
                    "audioUrl": audio_url,
                    "imageUrl": img_url,
                    "stems": stems_list,
                }
            },
        )
