"""Version of GeoKey."""

VERSION = (1, 0, 1, 'final', 0)


def get_version():
    """
    Return current version of GeoKey.

    Returns
    -------
    str
        Current version.
    """
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])

    sub = ''
    if VERSION[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[VERSION[3]] + str(VERSION[4])

    return version + sub
