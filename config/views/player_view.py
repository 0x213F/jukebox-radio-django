from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView


class PlayerView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        TODO
        """
        return self.template_response(request, 'pages/player.html', {})
