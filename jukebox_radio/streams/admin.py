from django.apps import apps
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

import pghistory

from jukebox_radio.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(apps.get_model('streams.Stream'))
class StreamAdmin(admin.ModelAdmin):

    # NOTE: https://github.com/jyveapp/django-pghistory
    object_history_template = 'admin/pghistory_template.html'

    def history_view(self, request, object_id, extra_context=None):
        '''
        Adds additional context for the custom history template.
        '''
        extra_context = extra_context or {}
        extra_context['object_history'] = (
            pghistory.models.AggregateEvent.objects
            .target(self.model(pk=object_id))
            .order_by('pgh_created_at')
            .select_related('pgh_context')
        )
        return super().history_view(
            request, object_id, extra_context=extra_context
        )


@admin.register(apps.get_model('streams.Queue'))
class QueueAdmin(admin.ModelAdmin):
    pass
