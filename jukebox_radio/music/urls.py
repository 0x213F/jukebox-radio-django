from django.urls import path

from jukebox_radio.music.views import MusicSearchView
from jukebox_radio.music.views import TrackCreateView
from jukebox_radio.music.views import TrackUpdateView


app_name = "music"
urlpatterns = [
    path("search/", view=MusicSearchView.as_view(), name="search"),
    path("track/create/", view=TrackCreateView.as_view(), name="track-create"),
]
