from django.urls import path

from jukebox_radio.streams.views.stream import (
    StreamGetView,
    StreamInitializeView,
    StreamPauseTrackView,
    StreamPlayTrackView,
    StreamPreviousTrackView,
    StreamScanBackwardView,
    StreamScanForwardView,
    StreamNextTrackView,
)
from jukebox_radio.streams.views.queue import (
    QueueCreateView,
    QueueDeleteView,
    QueueListView,
    QueueUpdateView,
)


app_name = "streams"
urlpatterns = [
    # Stream
    path(
        "stream/get/",
        view=StreamGetView.as_view(),
        name="stream-get",
    ),
    path(
        "stream/initialize/",
        view=StreamInitializeView.as_view(),
        name="stream-initialize",
    ),
    path(
        "stream/next-track/",
        view=StreamNextTrackView.as_view(),
        name="stream-next-track",
    ),
    path(
        "stream/pause-track/", view=StreamPauseTrackView.as_view(), name="stream-pause"
    ),
    path("stream/play-track/", view=StreamPlayTrackView.as_view(), name="stream-play"),
    path(
        "stream/previous-track/",
        view=StreamPreviousTrackView.as_view(),
        name="stream-previous-track",
    ),
    path(
        "stream/scan-backward/",
        view=StreamScanBackwardView.as_view(),
        name="stream-scan-backward",
    ),
    path(
        "stream/scan-forward/",
        view=StreamScanForwardView.as_view(),
        name="stream-scan-forward",
    ),
    # Queue
    path("queue/create/", view=QueueCreateView.as_view(), name="queue-create"),
    path("queue/delete/", view=QueueDeleteView.as_view(), name="queue-delete"),
    path("queue/list/", view=QueueListView.as_view(), name="queue-list"),
    path("queue/update/", view=QueueUpdateView.as_view(), name="queue-update"),
]
