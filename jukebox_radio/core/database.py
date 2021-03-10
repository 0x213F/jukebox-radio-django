import contextlib

from django_pglocks import advisory_lock


@contextlib.contextmanager
def acquire_playback_control_lock(stream):
    """
    Acquires a lock on a stream's playback controls (e.g. play, pause,
    skip, scan). If the lock is already taken, it waits for the lock to be
    free (up to 60 seconds).
    """
    lock_id = f"stream-{stream.uuid}"
    with advisory_lock(lock_id) as acquired:
        if not acquired:
            raise Exception("Lock not acquired")
        yield


@contextlib.contextmanager
def acquire_modify_queue_lock(stream):
    """
    Acquires a lock on a stream's queue (e.g. add, delete). If the lock is
    already taken, it waits for the lock to be free (up to 60 seconds).
    """
    lock_id = f"queue-{stream.uuid}"
    with advisory_lock(lock_id) as acquired:
        if not acquired:
            raise Exception("Lock not acquired")
        yield


@contextlib.contextmanager
def acquire_manage_queue_intervals_lock(queue_uuid):
    """
    Acquires a lock on a queues's intervals (e.g. add, delete). If the lock
    is already taken, it waits for the lock to be free (up to 60 seconds).
    """
    lock_id = f"queue-interval-{queue_uuid}"
    with advisory_lock(lock_id) as acquired:
        if not acquired:
            raise Exception("Lock not acquired")
        yield
