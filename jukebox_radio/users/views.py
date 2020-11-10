from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


class UserConnectSpotifyView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Spotify redirects a user to this URL after the Spotify authorization
        process.
        """
        code = request.GET.get("code", None)

        current_site = get_current_site(request)
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"https://{current_site}/users/user/connect-spotify/",
                "client_id": secrets.SPOTIFY_CLIENT_ID,
                "client_secret": secrets.SPOITFY_CLIENT_SECRET,
            },
        )
        response_json = response.json()

        cipher_suite = Fernet(secrets.FERNET_KEY)
        encoded_spotify_access_token = cipher_suite.encrypt(response_json["access_token"])
        encoded_spotify_refresh_token = cipher_suite.encrypt(response_json["refresh_token"])

        user = request.user
        user.encoded_spotify_access_token = encoded_spotify_access_token
        user.encoded_spotify_refresh_token = encoded_spotify_refresh_token
        user.spotify_scope = secrets.SPOTIFY_SCOPE
        user.save()

        return self.http_response_200({})
