from django.urls import path

from jukebox_radio.streams.views.marker import (
    MarkerCreateView,
    MarkerDeleteView,
    MarkerListView,
)
from jukebox_radio.streams.views.queue import (
    QueueCreateView,
    QueueDeleteView,
    QueueListView,
)
from jukebox_radio.streams.views.queue_interval import (
    QueueIntervalCreateView,
    QueueIntervalDeleteView,
)
from jukebox_radio.streams.views.stream import (
    StreamGetView,
    StreamInitializeView,
    StreamNextTrackView,
    StreamPauseTrackView,
    StreamPlayTrackView,
    StreamPrevTrackView,
    StreamScanBackwardView,
    StreamScanForwardView,
)

app_name = "streams"
urlpatterns = [
    # Marker
    # --------------------------------------------------------------------------
    path(
        "marker/create/",
        view=MarkerCreateView.as_view(),
        name="marker-create",
    ),
    path(
        "marker/delete/",
        view=MarkerDeleteView.as_view(),
        name="marker-delete",
    ),
    path(
        "marker/list/",
        view=MarkerListView.as_view(),
        name="marker-list",
    ),
    # Stream
    # --------------------------------------------------------------------------
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
        "stream/prev-track/",
        view=StreamPrevTrackView.as_view(),
        name="stream-prev-track",
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
    # --------------------------------------------------------------------------
    path("queue/create/", view=QueueCreateView.as_view(), name="queue-create"),
    path("queue/delete/", view=QueueDeleteView.as_view(), name="queue-delete"),
    path("queue/list/", view=QueueListView.as_view(), name="queue-list"),
    # QueueInterval
    # --------------------------------------------------------------------------
    path(
        "queue-interval/create/",
        view=QueueIntervalCreateView.as_view(),
        name="queue-interval-create",
    ),
    path(
        "queue-interval/delete/",
        view=QueueIntervalDeleteView.as_view(),
        name="queue-interval-delete",
    ),
]
