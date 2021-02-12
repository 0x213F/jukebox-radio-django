from django.urls import path

from jukebox_radio.users.views import (
    UserConnectSpotifyView,
    UserConnectYouTubeView,
    UserGetSettingsView,
)

app_name = "users"
urlpatterns = [
    path(
        "user/connect-spotify/",
        view=UserConnectSpotifyView.as_view(),
        name="user-connect-spotify",
    ),
    path(
        "user/connect-youtube",
        view=UserConnectYouTube.as_view(),
        name="user-connect-youtube",
    ),
    path(
        "user/get-settings/",
        view=UserGetSettingsView.as_view(),
        name="user-get-settings",
    )
]
