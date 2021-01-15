from django.apps import apps
from django.contrib import admin


@admin.register(apps.get_model("streams.Marker"))
class MarkerAdmin(admin.ModelAdmin):
    pass
