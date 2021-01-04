from cryptography.fernet import Fernet

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model

from config import celery_app

from jukebox_radio.networking.actions import make_request

User = get_user_model()


@celery_app.task()
def refresh_spotify_access_tokens():
    Request = apps.get_model("networking", "Request")

    cipher_suite = Fernet(settings.FERNET_KEY)
    user_qs = User.objects.filter(encrypted_spotify_refresh_token__isnull=False)

    for user in user_qs:

        try:
            encrypted_token = user.encrypted_spotify_refresh_token
            encrypted_token_utf8 = encrypted_token.encode("utf-8")
            token_utf8 = cipher_suite.decrypt(encrypted_token_utf8)
            token = token_utf8.decode("utf-8")

            data = {
                "grant_type": "refresh_token",
                "refresh_token": token,
                "client_id": settings.SPOTIFY_CLIENT_ID,
                "client_secret": settings.SPOITFY_CLIENT_SECRET,
            }

            response = make_request(
                Request.TYPE_POST,
                "https://accounts.spotify.com/api/token",
                data=data,
                user=user,
            )
            response_json = response.json()

            token = response_json["access_token"]
            token_utf8 = token.encode("utf-8")
            encrypted_token_utf8 = cipher_suite.encrypt(token_utf8)
            encrypted_token = encrypted_token_utf8.decode("utf-8")

            user.encrypted_spotify_access_token = encrypted_token
            user.save()

        except Exception as e:
            print(e)
            user.encrypted_spotify_access_token = None
            user.encrypted_spotify_refresh_token = None
            user.spotify_scope = None
            user.save()
