from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from jukebox_radio.core.base_view import BaseView

User = get_user_model()


def generate_redirect_uri(request):
    domain_prefix = "https" if request.is_secure() else "http"
    current_site = request.get_host()
    endpoint = '/spotify'
    return f"{domain_prefix}://{current_site}{endpoint}"


def generate_spotify_authorization_uri(request):
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": generate_redirect_uri(request),
        "scope": ",".join(settings.SPOTIFY_USER_DATA_SCOPES),
    }
    query_str = urlencode(params)

    return f"https://accounts.spotify.com/authorize?{query_str}"
