import requests

from django.apps import apps
from django.conf import settings

import pgtrigger


@pgtrigger.ignore("networking.Request:protect_inserts")
def make_request(_type, url, data={}, headers={}, user=None):
    Request = apps.get_model("networking", "Request")

    if _type == Request.TYPE_GET:
        response = requests.get(url, params=data, headers=headers)
    elif _type == Request.TYPE_POST:
        response = requests.post(url, data=data)
    else:
        raise ValueError(f"Unexpected request type: {_type}")

    Request.objects.create(
        user=user,
        type=_type,
        url=url,
        data=data,
        code=response.status_code,
        response=response.json(),
    )

    return response
