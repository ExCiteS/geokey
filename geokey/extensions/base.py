extensions = {}


class ExtensionExists(BaseException):
    """
    Exception that is thrown when an extension is registered with the same
    id as another extension that is already registered.
    """
    pass


def register(ext_id, name, display_admin=False, superuser=False):
    """
    Registeres a new extension to the system.

    Parameters
    ----------
    ext_id : str
        Unique identifier for the extension
    name : str
        Human readable name of the extension
    display_admin : Boolean
        Indicates if the extension provides pages for the admin interface
    superuser : Boolean
        Indicates if the extentsion is available for superusers only

    Raises
    ------
    ExtensionExists
        if another extension with the same ext_id has already been registered
    """
    if ext_id in extensions.keys():
        raise ExtensionExists(
            'An extension with id %s has already been registered' % ext_id
        )

    extensions[ext_id] = {
        'ext_id': ext_id,
        'name': name,
        'display_admin': display_admin,
        'superuser': superuser,
        'index_url': ext_id + ':index'
    }
