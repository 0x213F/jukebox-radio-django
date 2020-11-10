from django.urls import path

from jukebox_radio.users.views import (
    UserConnectSpotifyView,
)

app_name = "users"
urlpatterns = [
    path(
        "user/connect-spotify/",
        view=UserConnectSpotifyView.as_view(),
        name="user-connect-spotify",
    ),
]
