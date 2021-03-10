from django.apps import apps
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

FIVE_MINUTES = 60 * 5


class VoiceRecordingGetFileView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Create a track from upload.
        """
        VoiceRecording = apps.get_model("comments", "VoiceRecording")

        voice_recording_uuid = request.GET.get("voiceRecordingUuid")

        voice_recording = VoiceRecording.objects.get(
            uuid=voice_recording_uuid,
            user=request.user,
        )

        if settings.APP_ENV == settings.APP_ENV_LOCAL:
            scheme = request.scheme
            host = request.get_host()
            audio_url = f"{scheme}://{host}{voice_recording.audio.url}"
        elif settings.APP_ENV == settings.APP_ENV_PROD:
            import boto3
            from botocore.client import Config

            s3_client = boto3.client(
                "s3", config=Config(signature_version="s3v4"), region_name="us-west-1"
            )
            audio_url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": "jukebox-radio-prod",
                    "Key": f"media/{voice_recording.audio.name}",
                },
                ExpiresIn=FIVE_MINUTES,
            )

        return self.http_react_response(
            "voiceRecording/loadFile",
            {
                "voiceRecording": {
                    "uuid": voice_recording_uuid,
                    "audioUrl": audio_url,
                }
            },
        )
