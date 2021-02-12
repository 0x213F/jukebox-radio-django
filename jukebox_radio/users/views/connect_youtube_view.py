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

class UserConnectYouTubeView(BaseView, LoginRequiredMixin):
  def get(self, request, **kwargs):
    """
    YouTube redirects a user to this URL after the Spotify authorization process.
    """
    Request = apps.get_model("networking", "Request")

    user = request.user

    error = request.GET.get("error", None)
    if error:
      return self.http_response_400()

    code = request.GET.get("code", None)

    domain_prefix = "https" if request.is_secure() else "http"
    current_site = request.get_host()
    data = {
      "grant_type":
      "authorization_code",
      "code": code,
      "redirect_uri": f"{domain_prefix}://{current_site}/users/user/connect-youtube/",
      "client_id": settings.YOUTUBE_CLIENT_ID,
      "client_secret": settings.YOUTUBE_CLIENT_SECRET,
    }

