from urllib.parse import urlencode

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin

from jukebox_radio.core.base_view import BaseView
from jukebox_radio.music.models import GLOBAL_PROVIDER_CHOICES
from jukebox_radio.music.utils import get_search_results


class MusicSearchView(BaseView, LoginRequiredMixin):
    def get(self, request, **kwargs):
        """
        Given a query, get relevant collections.
        """
        Track = apps.get_model("music", "Track")
        Collection = apps.get_model("music", "Collection")

        providers = request.GET.get("providers").split(',')
        formats = request.GET.get("formats").split(',')
        query = request.GET.get("query")

        search_results = []
        for (provider_slug, _) in GLOBAL_PROVIDER_CHOICES:
            if provider_slug not in providers:
                continue
            search_results.extend(
                get_search_results(request.user, provider_slug, query, formats)
            )

        return self.http_response_200(search_results)
