from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


def generate_spotify_authorization_uri(request):
    domain_prefix = "https" if request.is_secure() else "http"
    current_site = get_current_site(request)
    endpoint = reverse("users:user-connect-spotify")

    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": f"{domain_prefix}://{current_site}{endpoint}",
    }
    query_str = urlencode(params)

    return f"https://accounts.spotify.com/authorize?{query_str}"


class SettingsView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Load settings page for user
        """
        spotify_authorization_url = generate_spotify_authorization_uri(request)

        return self.template_response(
            request,
            "pages/settings.html",
            {
                "spotify_is_already_authorized": bool(
                    request.user.encrypted_spotify_access_token
                ),
                "spotify_authorization_url": spotify_authorization_url,
            },
        )
