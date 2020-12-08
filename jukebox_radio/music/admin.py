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

    ordering = ("number",)

    fields = ('list_track_name', 'list_track_number',)

    readonly_fields = ("list_track_name", "list_track_number",)

    def has_add_permission(self, request, obj=None):
        return False

    def list_track_name(self, obj):
        return obj.track.name
    list_track_name.short_description = 'TRACK NAME'

    def list_track_number(self, obj):
        return obj.number
    list_track_number.short_description = 'TRACK NUMBER'


@admin.register(apps.get_model("music.Track"))
class TrackAdmin(admin.ModelAdmin):

    search_fields = (
        "name",
        "artist_name",
        "album_name",
    )

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_change_permission(self, request, obj=None):
    #     return False


@admin.register(apps.get_model("music.Album"))
class AlbumAdmin(admin.ModelAdmin):

    inlines = (CollectionListingAdminInline,)

    # fieldsets = (
    #     (
    #         "JUKEBOX RADIO",
    #         {
    #             "fields": (
    #                 "jr_img",
    #                 "jr_name",
    #             ),
    #         },
    #     ),
    #     (
    #         "SPOTIFY",
    #         {
    #             "fields": (
    #                 "spotify_img",
    #                 "spotify_uri",
    #                 "spotify_name",
    #             ),
    #         },
    #     ),
    #     (
    #         "YOUTUBE",
    #         {
    #             "fields": (
    #                 "youtube_img",
    #                 "youtube_id",
    #                 "youtube_name",
    #             ),
    #         },
    #     ),
    # )

    search_fields = (
        "name",
        "artist_name",
        "external_id",
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

    # fieldsets = (
    #     (
    #         "JUKEBOX RADIO",
    #         {
    #             "fields": (
    #                 "jr_img",
    #                 "jr_name",
    #             ),
    #         },
    #     ),
    #     (
    #         "SPOTIFY",
    #         {
    #             "fields": (
    #                 "spotify_img",
    #                 "spotify_uri",
    #                 "spotify_name",
    #             ),
    #         },
    #     ),
    #     (
    #         "YOUTUBE",
    #         {
    #             "fields": (
    #                 "youtube_img",
    #                 "youtube_id",
    #                 "youtube_name",
    #             ),
    #         },
    #     ),
    # )

    search_fields = (
        "name",
        "artist_name",
        "external_id",
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
class SessionAdmin(admin.ModelAdmin):

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
