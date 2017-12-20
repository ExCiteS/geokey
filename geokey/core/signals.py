"""Core signals."""

from django.dispatch import Signal

delete_project = Signal(providing_args=["project"])

class RequestAccessorSignal(Signal):
    """Request accessor signal."""

    def __init__(self, providing_args=None):
        """Initiate the signal."""
        return Signal.__init__(self, providing_args)

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        """Connect the signal."""
        Signal.connect(self, receiver, sender, weak, dispatch_uid)


request_accessor = RequestAccessorSignal()


def get_request():
    """Get the current request."""
    entry = request_accessor.send(None)
    if entry:
        entry = entry[0]
        if entry:
            return entry[1]
    return None
