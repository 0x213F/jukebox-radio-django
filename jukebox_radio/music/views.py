from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView

from .utils import get_spotify_results
from .utils import get_youtube_results

User = get_user_model()


class TrackSearchView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Given a query, get relevant tracks.
        """
        spotify_results = get_spotify_results(query, "tracks", request.user)
        youtube_results = get_youtube_results(query, "tracks")
        jr_results = get_jr_results()

        results = spotify_results + youtube_results + jr_results
        return self.http_response_200(results)


class CollectionSearchView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Given a query, get relevant collections.
        """

        spotify_results = get_spotify_results(query, "collections", request.user)
        youtube_results = get_youtube_results(query, "collections")
        jr_results = get_jr_results()

        results = spotify_results + youtube_results + jr_results
        return self.http_response_200(results)
