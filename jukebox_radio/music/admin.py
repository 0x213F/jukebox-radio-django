from django.apps import apps
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

import pghistory

User = get_user_model()


class CollectionListingAdminInline(admin.TabularInline):
    model = apps.get_model("music.CollectionListing")
    fk_name = "collection"
    extra = 0

    readonly_fields = ("number",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(apps.get_model("music.Track"))
class TrackAdmin(admin.ModelAdmin):
    pass

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_change_permission(self, request, obj=None):
    #     return False


@admin.register(apps.get_model("music.Album"))
class AlbumAdmin(admin.ModelAdmin):

    inlines = (CollectionListingAdminInline,)

    fieldsets = (
        (
            "JUKEBOX RADIO",
            {
                "fields": (
                    "jr_img",
                    "jr_name",
                ),
            },
        ),
        (
            "SPOTIFY",
            {
                "fields": (
                    "spotify_img",
                    "spotify_uri",
                    "spotify_name",
                ),
            },
        ),
        (
            "YOUTUBE",
            {
                "fields": (
                    "youtube_img",
                    "youtube_id",
                    "youtube_name",
                ),
            },
        ),
    )

    search_fields = (
        "jr_name",
        "jr_duration_ms",
        "spotify_uri",
        "spotify_name",
        "spotify_duration_ms",
        "youtube_id",
        "youtube_name",
        "youtube_duration_ms",
    )

    def get_queryset(self, request):
        Collection = apps.get_model("music.Collection")

        qs = Collection.objects.all()
        qs = qs.filter(format=Collection.FORMAT_ALBUM)
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(apps.get_model("music.Playlist"))
class PlaylistAdmin(admin.ModelAdmin):

    inlines = (CollectionListingAdminInline,)

    fieldsets = (
        (
            "JUKEBOX RADIO",
            {
                "fields": (
                    "jr_img",
                    "jr_name",
                ),
            },
        ),
        (
            "SPOTIFY",
            {
                "fields": (
                    "spotify_img",
                    "spotify_uri",
                    "spotify_name",
                ),
            },
        ),
        (
            "YOUTUBE",
            {
                "fields": (
                    "youtube_img",
                    "youtube_id",
                    "youtube_name",
                ),
            },
        ),
    )

    search_fields = (
        "jr_name",
        "spotify_uri",
        "spotify_name",
        "youtube_id",
        "youtube_name",
    )

    def get_queryset(self, request):
        Collection = apps.get_model("music.Collection")

        qs = Collection.objects.all()
        qs = qs.filter(format=Collection.FORMAT_PLAYLIST)
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(apps.get_model("music.Session"))
class MixAdmin(admin.ModelAdmin):

    inlines = (CollectionListingAdminInline,)

    fieldsets = (
        (
            "JUKEBOX RADIO",
            {
                "fields": (
                    "jr_img",
                    "jr_name",
                ),
            },
        ),
        (
            "SPOTIFY",
            {
                "fields": (
                    "spotify_img",
                    "spotify_uri",
                    "spotify_name",
                ),
            },
        ),
        (
            "YOUTUBE",
            {
                "fields": (
                    "youtube_img",
                    "youtube_id",
                    "youtube_name",
                ),
            },
        ),
    )

    search_fields = (
        "jr_name",
        "jr_duration_ms",
        "spotify_uri",
        "spotify_name",
        "spotify_duration_ms",
        "youtube_id",
        "youtube_name",
        "youtube_duration_ms",
    )

    def get_queryset(self, request):
        Collection = apps.get_model("music", "Collection")

        qs = Collection.objects.all()
        qs = qs.filter(format=Collection.FORMAT_SESSION)
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
