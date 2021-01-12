from django.utils import timezone


def ms(td):
    """
    Get milliseconds from timedelta.
    """
    return td.total_seconds() * 1000


def now():
    """
    Get now as an UTC timestamp.
    """
    return timezone.now()


def epoch(dt):
    """
    Get milliseconds since epoch.
    """
    return int(dt.timestamp() * 1000)
