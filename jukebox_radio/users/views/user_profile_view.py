from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

User = get_user_model()

class UserGetProfileView(BaseView, LoginRequiredMixin):
  def get(self, request, **kwargs):
    """
    Get user profile.
    """
    username = self.param(request, "username")

    return self.http_response_200({
      "user": {
        "can_edit": username == request.user.username,
        "profile_image": request.user.userprofile.profile_image,
        "description": request.user.userprofile.description,
        "website": request.user.userprofile.website
      }
    })