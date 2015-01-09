extensions = {}


class ExtensionExists(BaseException):
    pass


def register(ext_id, name, admin):
    if ext_id in extensions.keys():
        raise ExtensionExists(
            'An extension with id %s has already been registered' % ext_id
        )

    extensions[ext_id] = {
        'ext_id': ext_id,
        'name': name,
        'display_admin': admin,
        'index_url': ext_id + ':index'
    }
