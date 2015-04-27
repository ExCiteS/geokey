#!/usr/bin/env python

from setuptools import setup, find_packages
from geokey.version import get_version


def get_install_requires():
    """
    parse requirements.txt, ignore links, exclude comments
    """
    requirements = list()
    for line in open('requirements.txt').readlines():
        # skip to next iteration if comment or empty line
        if line.startswith('#') or line.startswith('git+https') or line == '':
            continue
        # add line to requirements
        requirements.append(line.rstrip())

    return requirements

setup(
    name="geokey",
    version=get_version(),
    license="Apache 2.0",
    description="Open-source participatory mapping framework",
    url='http://geokey.org.uk',
    download_url='https://github.com/excites/geokey/releases',
    author="Oliver Roick",
    author_email="o.roick@ucl.ac.uk",
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=get_install_requires(),
    include_package_data=True,
)
