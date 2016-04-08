"""Base for extensions."""

from geokey.extensions.exceptions import ExtensionExists


extensions = {}


def register(ext_id, name, display_admin=False, superuser=False, version=None):
    """
    Register a new extension on the system.

    Parameters
    ----------
    ext_id : str
        Unique identifier for the extension.
    name : str
        Human readable name of the extension.
    display_admin : bool
        Indicates if the extension provides pages for the admin interface.
    superuser : bool
        Indicates if the extentsion is available for superusers only.
    version : str
        Version of the extension (optional).

    Raises
    ------
    ExtensionExists
        When another extension with the same `ext_id` has already been
        registered.
    """
    if ext_id in extensions.keys():
        raise ExtensionExists(
            'An extension with ID %s has already been registered.' % ext_id
        )

    extensions[ext_id] = {
        'ext_id': ext_id,
        'name': name,
        'version': version,
        'display_admin': display_admin,
        'superuser': superuser,
        'index_url': ext_id + ':index'
    }


def deregister(ext_id):
    """
    Deregister an extension from the system.

    Only to be used for testing.

    Parameters
    ----------
    ext_id : str
        Unique identifier for the extension.
    """
    extensions.pop(ext_id, None)
