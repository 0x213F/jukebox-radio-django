from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.utils import generate_spotify_authorization_uri

User = get_user_model()


class UserGetSettingsView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Get the settings of a user.
        """
        return self.http_response_200({
            "spotify": {
                "authorizationUrl": generate_spotify_authorization_uri(request),
                "accessToken": request.user.spotify_access_token,
            },
            "idleQueue": request.user.idle_after_now_playing,
            "speakVoice": request.user.mute_voice_recordings,
            "focusMode": request.user.focus_mode
        })
