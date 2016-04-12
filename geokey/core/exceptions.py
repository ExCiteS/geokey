"""Core exceptions."""


class Unauthenticated(Exception):
    """Thrown when user is not authenticated."""

    pass


class MalformedRequestData(Exception):
    """Thrown when request data is malformed."""

    pass


class InputError(Exception):
    """Thrown on input error."""

    pass


class FileTypeError(Exception):
    """Thrown on file type error."""

    pass
