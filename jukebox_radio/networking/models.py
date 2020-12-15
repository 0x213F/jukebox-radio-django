import pgtrigger
import uuid

from django.db import models

import pgtrigger


@pgtrigger.register(
    pgtrigger.Protect(
        name="protect_inserts",
        operation=pgtrigger.Insert,
    )
)
@pgtrigger.register(
    pgtrigger.Protect(
        name="append_only",
        operation=(pgtrigger.Update | pgtrigger.Delete),
    )
)
class Request(models.Model):

    TYPE_GET = 'get'
    TYPE_POST = 'post'
    TYPE_CHOICES = (
        (TYPE_GET, 'GET'),
        (TYPE_POST, 'POST'),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)

    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    url = models.URLField(max_length=200)
    data = models.JSONField()

    code = models.PositiveIntegerField()
    response = models.JSONField()