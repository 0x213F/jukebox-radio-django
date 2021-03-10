from datetime import datetime, timedelta

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef, Q

from jukebox_radio.music.tasks import generate_stems_for_track


class Command(BaseCommand):
    help = "Generate stems"

    def handle(self, *args, **options):
        Stem = apps.get_model("music", "Stem")
        Track = apps.get_model("music", "Track")

        tracks = (
            Track
            .objects
            .filter(provider=Track.PROVIDER_JUKEBOX_RADIO)
            .exclude(
                Exists(Stem.objects.filter(track_id=OuterRef("uuid")))
            )
        )

        generate_stems_for_track.delay(str(tracks.latest('created_at').uuid))
