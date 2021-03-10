from django.urls import path

from jukebox_radio.music.views import (
    MusicSearchView,
    TrackCreateView,
    TrackGetFilesView,
)

app_name = "music"
urlpatterns = [
    path("search/", view=MusicSearchView.as_view(), name="search"),
    path("track/create/", view=TrackCreateView.as_view(), name="track-create"),
    path("track/get-files/", view=TrackGetFilesView.as_view(), name="track-get-files"),
]
