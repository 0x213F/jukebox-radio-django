import math

import pghistory

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import mark_safe

from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_CHOICES

User = get_user_model()


class CollectionListingAdminInline(admin.TabularInline):
    model = apps.get_model("music.CollectionListing")
    fk_name = "collection"
    extra = 0

    ordering = ("number",)

    fields = ('list_track_name', 'list_track_number',)

    readonly_fields = ("list_track_name", "list_track_number",)

    def has_add_permission(self, request, obj=None):
        return False

    def list_track_name(self, obj):
        url = reverse(f'admin:music_collectionlisting', obj.id)
        return mark_safe(f'<a href="{url}">{obj.track.name}</a>')
    list_track_name.short_description = 'TRACK NAME'

    def list_track_number(self, obj):
        return obj.number
    list_track_number.short_description = 'TRACK NUMBER'


class ProviderListFilter(admin.SimpleListFilter):
    title = 'provider'
    parameter_name = 'provider'

    def lookups(self, request, model_admin):
        return GLOBAL_PROVIDER_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(provider=value)


class TrackFormatListFilter(admin.SimpleListFilter):
    title = 'format'
    parameter_name = 'format'

    def lookups(self, request, model_admin):
        return GLOBAL_PROVIDER_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(format=value)


class TrackHasDurationFilter(admin.SimpleListFilter):
    title = 'has duration'
    parameter_name = 'has_duration'

    YES = 'yes'
    NO = 'no'

    def lookups(self, request, model_admin):
        return (
            (True, 'Yes'),
            (False, 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        print(value)
        if not value:
            return queryset

        print(value)

        if value == 'True':
            return queryset.filter(duration_ms__isnull=False)
        elif value == 'False':
            return queryset.filter(duration_ms__isnull=True)
        else:
            raise Exception('Invalid choice')


@admin.register(apps.get_model("music.Track"))
class TrackAdmin(admin.ModelAdmin):
    list_filter = (ProviderListFilter, TrackFormatListFilter, TrackHasDurationFilter,)

    list_display = (
        'name',
        'album_name',
        'artist_name',
        'list_duration',
        'list_image',
        'provider',
        'format',
    )

    search_fields = (
        "uuid",
        "user__email",
        "name",
        "album_name",
        "artist_name",
        "external_id",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def list_duration(self, obj):
        if not obj.duration_ms:
            return ''

        vals = []

        hours = math.floor(obj.duration_ms / (1000 * 60 * 60))
        if hours:
            vals.append(f'{hours} hours')

        minutes = math.floor(obj.duration_ms / (1000 * 60))
        if minutes:
            vals.append(f'{minutes} minutes')

        seconds = obj.duration_ms % (1000 * 60) / 1000
        if seconds:
            vals.append(f'{seconds} seconds')

        return ' '.join(vals)

    def list_image(self, obj):
        url = obj.img_url or obj.img.url
        return mark_safe(f'<img src="{url}" style="height: 15px;" />')
