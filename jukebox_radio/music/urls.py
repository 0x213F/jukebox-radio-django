from django.urls import path

from jukebox_radio.music.views import (
    TrackSearchView,
    CollectionSearchView
)


app_name = "music"
urlpatterns = [
    path("track/search/", view=TrackSearchView.as_view(), name="track-search"),
    path("collection/search/", view=CollectionSearchView.as_view(), name="collection-search"),
]
