from cryptography.fernet import Fernet

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.core.utils import generate_spotify_authorization_uri
from jukebox_radio.networking.actions import make_request

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
            }
        })
