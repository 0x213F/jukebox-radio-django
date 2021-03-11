from cryptography.fernet import Fernet
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.utils import generate_redirect_uri
from jukebox_radio.networking.actions import make_request

User = get_user_model()


class UserConnectSpotifyView(BaseView, LoginRequiredMixin):
    def post(self, request, **kwargs):
        """
        Spotify redirects a user to this URL after the Spotify authorization
        process.
        """
        Request = apps.get_model("networking", "Request")

        user = request.user

        code = self.param(request, "code")
        error = self.param(request, "error")

        if error:
            return self.http_response_400(error)

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": generate_redirect_uri(request),
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOITFY_CLIENT_SECRET,
        }

        response = make_request(
            Request.TYPE_POST,
            "https://accounts.spotify.com/api/token",
            data=data,
            user=user,
        )
        response_json = response.json()

        cipher_suite = Fernet(settings.FERNET_KEY)

        token = response_json["access_token"]
        token_utf8 = token.encode("utf-8")
        encrypted_token_utf8 = cipher_suite.encrypt(token_utf8)
        encrypted_token = encrypted_token_utf8.decode("utf-8")
        user.encrypted_spotify_access_token = encrypted_token

        token = response_json["refresh_token"]
        token_utf8 = token.encode("utf-8")
        encrypted_token_utf8 = cipher_suite.encrypt(token_utf8)
        encrypted_token = encrypted_token_utf8.decode("utf-8")
        user.encrypted_spotify_refresh_token = encrypted_token

        user.spotify_scope = ",".join(settings.SPOTIFY_USER_DATA_SCOPES)
        user.save()

        return self.http_response_200()
