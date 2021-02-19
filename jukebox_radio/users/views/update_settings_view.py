from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect

from jukebox_radio.core.base_view import BaseView


class UserUpdateSettingsView(BaseView, LoginRequiredMixin):

    def post(self, request):

        user = request.user
        field = self.param(request, 'field')
        value = self.param(request, 'value')

        allowed_field_values = [
            "idle_after_now_playing",
            "mute_voice_recordings",
            "focus_mode",
        ]
        if field not in allowed_field_values:
            raise Exception(f'You are not allowed to change {field}')

        setattr(user, field, value)
        user.save()

        return self.http_response_200()
