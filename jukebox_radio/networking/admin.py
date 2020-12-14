from django.apps import apps
from django.contrib import admin


@admin.register(apps.get_model("networking.Request"))
class RequestAdmin(admin.ModelAdmin):
    pass
