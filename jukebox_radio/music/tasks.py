from config import celery_app


def get_chunk_temporary_filename(track_uuid, idx):
    return f"./garbage/segment-{idx}-{track_uuid}"


@celery_app.task()
def generate_stems_for_track(track_uuid):
    import os
    import shutil
    import tempfile
    import uuid

    from django.apps import apps
    from django.conf import settings
    from django.core.files import File
    from pydub import AudioSegment
    from pydub.utils import make_chunks
    from spleeter.separator import Separator

    Track = apps.get_model("music", "Track")
    Stem = apps.get_model("music", "Stem")

    track = Track.objects.get(uuid=track_uuid)

    if track.provider != Track.PROVIDER_JUKEBOX_RADIO:
        raise ValueError("Track must be of provider Jukebox Radio to create stems")
    if not track.audio:
        raise ValueError("Track must have an audio track to create stems")

    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(track.audio.read())

    # NOTE: Spleeter *should* be able to load .ogg files for direct conversion.
    #       I could not get that working, so first I convert to .wav.
    ext = "wav"
    track_uuid = track_uuid
    base_filename = f"./garbage/master-{track_uuid}.{ext}"
    audio_segment = AudioSegment.from_ogg(f.name)
    audio_segment.export(base_filename, format=ext)

    # NOTE: Spleeter crashes when processing large audio files, likely due to
    #       the system not having enough RAM. Here we chunk it into smaller
    #       sizes for processing.
    #
    #       If your system is silently crashing, it is likely running out of
    #       RAM. Combat the issue by adjusting the enviorment variable value
    #       for AUDIO_SEGMENT_PROCESSING_LENGTH to a smaller value.
    separator = Separator("spleeter:4stems")
    chunks = make_chunks(audio_segment, settings.AUDIO_SEGMENT_PROCESSING_LENGTH)
    wav_codec = "wav"
    export_codec = "ogg"
    for idx in range(len(chunks)):
        chunk = chunks[idx]
        chunk_filename = get_chunk_temporary_filename(track_uuid, idx)
        chunk_filename_with_ext = f"{chunk_filename}.{wav_codec}"
        chunk.export(chunk_filename_with_ext, format=wav_codec)

    for idx in range(len(chunks)):
        chunk = chunks[idx]
        chunk_filename = get_chunk_temporary_filename(track_uuid, idx)
        chunk_filename_with_ext = f"{chunk_filename}.{wav_codec}"
        separator.separate_to_file(
            chunk_filename_with_ext, "./garbage/", codec=export_codec
        )

    # Stitch the audio segments back together
    stem_audio_segments = {
        f"bass.{export_codec}": AudioSegment.empty(),
        f"drums.{export_codec}": AudioSegment.empty(),
        f"other.{export_codec}": AudioSegment.empty(),
        f"vocals.{export_codec}": AudioSegment.empty(),
    }
    for idx in range(len(chunks)):
        chunk_filename = get_chunk_temporary_filename(track_uuid, idx)
        for stem_audio_key in stem_audio_segments.keys():
            audio_segment = AudioSegment.from_ogg(f"{chunk_filename}/{stem_audio_key}")
            stem_audio_segments[stem_audio_key] += audio_segment

    # Export stems
    for stem_audio_key, stem_audio_segment in stem_audio_segments.items():
        full_stem_filename = f"./garbage/final-{track_uuid}-{stem_audio_key}"
        audio_file = File(
            stem_audio_segment.export(full_stem_filename, format=export_codec)
        )

        instrument = None
        if Stem.INSTRUMENT_BASS in stem_audio_key:
            instrument = Stem.INSTRUMENT_BASS
        elif Stem.INSTRUMENT_DRUMS in stem_audio_key:
            instrument = Stem.INSTRUMENT_DRUMS
        elif Stem.INSTRUMENT_VOCALS in stem_audio_key:
            instrument = Stem.INSTRUMENT_VOCALS
        else:  # Stem.INSTRUMENT_OTHER in stem_audio_key:
            instrument = Stem.INSTRUMENT_OTHER

        Stem.objects.create(
            track=track,
            instrument=instrument,
            audio=audio_file,
        )

        os.remove(full_stem_filename)

    # Delete remaining temporary files
    os.remove(base_filename)
    for idx in range(len(chunks)):
        chunk_filename = get_chunk_temporary_filename(track_uuid, idx)
        shutil.rmtree(chunk_filename)
        chunk_filename_with_ext = f"{chunk_filename}.{wav_codec}"
        os.remove(chunk_filename_with_ext)

    print("DONE!")
