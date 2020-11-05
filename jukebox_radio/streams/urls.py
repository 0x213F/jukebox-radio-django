from django.urls import path

from jukebox_radio.streams.views.stream import (
    StreamPauseTrackView,
    StreamPlayTrackView,
    StreamRewindTrackView,
    StreamScanBackwardView,
    StreamScanForwardView,
    StreamSkipTrackView,
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
    path("stream/pausetrack/", view=StreamPauseTrackView.as_view(), name="stream-pause"),
    path("stream/playtrack/", view=StreamPlayTrackView.as_view(), name="stream-play"),
    path("stream/rewindtrack/", view=StreamRewindTrackView.as_view(), name="stream-rewind-track"),
    path("stream/scanbackward/", view=StreamScanBackwardView.as_view(), name="stream-scan-backward"),
    path("stream/scanforward/", view=StreamScanForwardView.as_view(), name="stream-scan-forward"),
    path("stream/skiptrack/", view=StreamSkipTrackView.as_view(), name="stream-skip-track"),
    # Queue
    path("queue/create/", view=QueueCreateView.as_view(), name="queue-create"),
    path("queue/delete/", view=QueueDeleteView.as_view(), name="queue-delete"),
    path("queue/list/", view=QueueListView.as_view(), name="queue-list"),
    path("queue/update/", view=QueueUpdateView.as_view(), name="queue-update"),
]
