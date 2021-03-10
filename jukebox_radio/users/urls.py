from django.urls import path

from jukebox_radio.users.views import (
    UserConnectSpotifyView,
    UserGetSettingsView,
    UserUpdateSettingsView,
)

app_name = "users"
urlpatterns = [
    path(
        "user/connect-spotify/",
        view=UserConnectSpotifyView.as_view(),
        name="user-connect-spotify",
    ),
    path(
        "user/get-settings/",
        view=UserGetSettingsView.as_view(),
        name="user-get-settings",
    ),
    path(
        "user/update-settings/",
        view=UserUpdateSettingsView.as_view(),
        name="user-update-settings",
    ),
]
