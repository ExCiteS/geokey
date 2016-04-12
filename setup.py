#!/usr/bin/env python

"""GeoKey setup."""

from os.path import join
from setuptools import setup, find_packages

from geokey.version import get_version


name = 'geokey'
version = get_version()
repository = join('https://github.com/ExCiteS', name)


def get_install_requires():
    """
    Get requirements (ignore links, exclude comments).

    Returns
    -------
    list
        Requirements for GeoKey.
    """
    requirements = list()
    for line in open('requirements.txt').readlines():
        if line.startswith('#') or line.startswith('git+https') or line == '':
            continue
        requirements.append(line.rstrip())
    return requirements


setup(
    name=name,
    version=version,
    description='Platform for participatory mapping',
    url='http://geokey.org.uk',
    download_url=join(repository, 'tarball', version),
    author='ExCiteS',
    author_email='excites@ucl.ac.uk',
    license='Apache 2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_install_requires(),
)
