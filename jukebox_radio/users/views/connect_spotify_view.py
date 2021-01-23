from cryptography.fernet import Fernet

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.networking.actions import make_request

User = get_user_model()


class UserConnectSpotifyView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Spotify redirects a user to this URL after the Spotify authorization
        process.
        """
        Request = apps.get_model("networking", "Request")

        user = request.user

        error = request.GET.get("error", None)
        if error:
            messages.add_message(
                request, messages.ERROR, "Spotify authentication failed"
            )
            return self.http_response_400()

        code = request.GET.get("code", None)

        domain_prefix = "https" if request.is_secure() else "http"
        current_site = request.get_host()
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"{domain_prefix}://{current_site}/users/user/connect-spotify/",
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

        user.spotify_scope = settings.SPOTIFY_USER_DATA_SCOPES
        user.save()

        return self.http_response_200()
