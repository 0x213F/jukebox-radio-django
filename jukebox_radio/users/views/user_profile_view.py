from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()

class UserGetProfileView(BaseView, LoginRequiredMixin):
  def get(self, request, **kwargs):
    """
    Get user profile.
    """

    return self.http_response_200({

    })