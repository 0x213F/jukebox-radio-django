from django.urls import path

from jukebox_radio.comments.views.textcomment import (
    TextCommentCreateView,
    TextCommentDeleteView,
    TextCommentUpdateView,
)
from jukebox_radio.comments.views.textcommentmodification import (
    TextCommentModificationCreateView,
    TextCommentModificationListDeleteView,
)
from jukebox_radio.comments.views.voicerecording import (
    VoiceRecordingCreateView,
    VoiceRecordingDeleteView,
    VoiceRecordingGetView,
    VoiceRecordingListView,
)


app_name = "comments"
urlpatterns = [
    # TextComment
    path(
        "text-comment/create/",
        view=TextCommentCreateView.as_view(),
        name="text-comment-create",
    ),
    path(
        "text-comment/delete/",
        view=TextCommentDeleteView.as_view(),
        name="text-comment-delete",
    ),
    path(
        "text-comment/update/",
        view=TextCommentUpdateView.as_view(),
        name="text-comment-update",
    ),
    # TextCommentModification
    path(
        "text-comment-modification/create/",
        view=TextCommentModificationCreateView.as_view(),
        name="text-comment-modification-create",
    ),
    path(
        "text-comment-modification/list-delete/",
        view=TextCommentModificationListDeleteView.as_view(),
        name="text-comment-modification-list-delete",
    ),
    # VoiceRecording
    path(
        "voice-recording/create/",
        view=VoiceRecordingCreateView.as_view(),
        name="voice-recording-create",
    ),
    path(
        "voice-recording/delete/",
        view=VoiceRecordingDeleteView.as_view(),
        name="voice-recording-delete",
    ),
    path(
        "voice-recording/get/",
        view=VoiceRecordingGetView.as_view(),
        name="voice-recording-get",
    ),
    path(
        "voice-recording/list/",
        view=VoiceRecordingListView.as_view(),
        name="voice-recording-list",
    ),
]
