import uuid

import pgtrigger
from django.db import models
from unique_upload import unique_upload


def upload_to_stems_audios(*args, **kwargs):
    return f"django-storage/music/stems/audios/" f"{unique_upload(*args, **kwargs)}"


@pgtrigger.register(
    pgtrigger.Protect(
        name="protect_delete",
        operation=pgtrigger.Delete,
    )
)
class Stem(models.Model):
    """
    An isolated part of a track. Only Jukebox Radio tracks may have stems. For
    example: an audio file containing just the drums of an uploaded track.
    """

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
        related_name="stems",
    )

    instrument = models.CharField(max_length=32, choices=INSTRUMENT_CHOICES)

    audio = models.FileField(upload_to=upload_to_stems_audios)

    def __str__(self):
        return str(self.uuid)
