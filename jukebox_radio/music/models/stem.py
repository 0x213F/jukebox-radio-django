import uuid

from django.db import models

import pgtrigger
from unique_upload import unique_upload

from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_SPOTIFY
from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_YOUTUBE
from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_JUKEBOX_RADIO
from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_CHOICES


def upload_to_stems_audios(*args, **kwargs):
    return f"django-storage/music/stems/audios/" f"{unique_upload(*args, **kwargs)}"


@pgtrigger.register(
    pgtrigger.Protect(
        name="protect_delete",
        operation=pgtrigger.Delete,
    )
)
class Stem(models.Model):
    INSTRUMENT_BASS = "bass"
    INSTRUMENT_DRUMS = "drums"
    INSTRUMENT_VOCALS = "vocals"
    INSTRUMENT_OTHER = "other"
    INSTRUMENT_CHOICES = (
        (INSTRUMENT_BASS, "Bass"),
        (INSTRUMENT_DRUMS, "Drums"),
        (INSTRUMENT_VOCALS, "Vocals"),
        (INSTRUMENT_OTHER, "Other"),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    track = models.ForeignKey(
        "music.Track",
        on_delete=models.CASCADE,
    )

    instrument = models.CharField(max_length=32, choices=INSTRUMENT_CHOICES)

    audio = models.FileField(upload_to=upload_to_stems_audios)

    def __str__(self):
        return self.uuid
