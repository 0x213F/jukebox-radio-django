from django.urls import path

from jukebox_radio.music.views import MusicSearchView


app_name = "music"
urlpatterns = [
    path("search/", view=MusicSearchView.as_view(), name="search"),
]
