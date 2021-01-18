from django.apps import apps
from django.contrib import admin


@admin.register(apps.get_model("streams.QueueInterval"))
class QueueIntervalAdmin(admin.ModelAdmin):
    pass
