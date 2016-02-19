.. image:: https://img.shields.io/pypi/v/geokey.svg
    :alt: PyPI Package
    :target: https://pypi.python.org/pypi/geokey

.. image:: https://img.shields.io/travis/ExCiteS/geokey/master.svg
    :alt: Travis CI Build Status
    :target: https://travis-ci.org/ExCiteS/geokey

.. image:: https://coveralls.io/repos/ExCiteS/geokey/badge.svg?branch=master&service=github
    :alt: Coveralls Test Coverage
    :target: https://coveralls.io/github/ExCiteS/geokey?branch=master

.. image:: https://requires.io/github/ExCiteS/geokey/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/ExCiteS/geokey/requirements/?branch=master


======
GeoKey
======

GeoKey is a platform for participatory mapping, that is developed by `Extreme Citizen Science <http://ucl.ac.uk/excites>`_ research group at University College London.


Install for development
=======================

GeoKey can be run on Python 2.7 only.

1. Update your system:

.. code-block:: console

    sudo apt-get update && sudo apt-get upgrade

2. Install Postgres and PostGIS (we follow the `official guides <http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS21UbuntuPGSQL93Apt>`_):

.. code-block:: console

    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt wheezy-pgdg main" >> /etc/apt/sources.list'
    wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install postgresql-9.4-postgis-2.1 postgresql-contrib postgresql-server-dev-9.4

3. Setup all other dependencies:

.. code-block:: console

    sudo apt-get install python-pip python-virtualenv python-dev libjpeg-dev binutils libproj-dev libav-tools gdal-bin python-gdal

For Ubuntu you might also need to install *libavcodec-extra-52* or *libavcodec-extra-53*.


Setup database
==============

1. For simplicity, switch to user *postgres*:

.. code-block:: console

    sudo su - postgres

2. Install postgis in template1 (only required for running tests):

.. code-block:: console

    psql -d template1 -c 'create extension hstore;'

3. Log in to the database:

.. code-block:: console

    psql

4. Create the user (replace *django* with your user):

.. code-block:: console

    postgres=# CREATE USER django WITH PASSWORD 'django123';

5. Make created user a superuser on your database (this is required for tests only and shouldn't be done in production):

.. code-block:: console

    postgres=# ALTER ROLE django WITH superuser;

6. Create the database (replace *django* with your user and *geokey* with a desired name for the database):

.. code-block:: console

    postgres=# CREATE DATABASE geokey OWNER django;

7. Log out and connect to the database:

.. code-block:: console

    postgres=# \q
    psql -d geokey

8. Install the required extensions:

.. code-block:: console

    geokey=# CREATE EXTENSION postgis;
    geokey=# CREATE EXTENSION hstore;

9. Logout of the database and a user:

.. code-block:: console

    geokey=# \q
    logout


Setup GeoKey
============

1. Clone the repository:

.. code-block:: console

    git clone https://github.com/ExCiteS/geokey.git

2. Install the package and development requirements:

.. code-block:: console

    cd geokey
    pip install -e .
    pip install -r requirements.txt
    pip install -r requirements-dev.txt

You may need to add *sudo* before the pip commands, unless you are logged in as root or working within a virtual environment.

3. Copy the directory *local_settings.example* to *local_settings*

.. code-block:: console

  cp -r local_settings.example local_settings

4. Inside the *local_settings* open *settings.py* in a text editor and...

Add your `database settings <https://docs.djangoproject.com/en/1.8/ref/settings/#databases>`_:

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'geokey',
            'USER': 'django',
            'PASSWORD': 'xxxxxxxxx',
            'HOST': 'host',  # usually 'localhost'
            'PORT': ''
        }
    }

Set the `secret key <https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-SECRET_KEY>`_:

.. code-block:: python

    SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'


Set the `STATIC_ROOT directory <https://docs.djangoproject.com/en/1.8/howto/static-files/#deployment>`_:

.. code-block:: python

  STATIC_ROOT = '/some/path/'

5. Migrate the database:

.. code-block:: console

    python manage.py migrate

6. Add yourself as a superuser (you can use the same email and password to log into the system later):

.. code-block:: console

    python manage.py createsuperuser

7. Run the *collectstatic* management command:

.. code-block:: console

    python manage.py collectstatic


Run the test server
-------------------

.. code-block:: console

    python manage.py runserver 0.0.0.0:8000


Run tests
---------

.. code-block:: console

    python manage.py test

Running tests will remove all uploaded images of contributions from the assets directory. If you require to keep them, please use custom test settings with a *--settings* flag.


We use open-source technologies
===============================

GeoKey was built using some amazing open-source technology. We would like to thank all contributors to these projects:

- `Django <https://www.djangoproject.com/>`_
- `django-rest-framework <http://www.django-rest-framework.org/>`_
- `django-rest-framework-gis <https://github.com/djangonauts/django-rest-framework-gis>`_
- `django-hstore <https://github.com/djangonauts/django-hstore>`_
- `django-braces <https://github.com/brack3t/django-braces>`_
- `django-pgjson <https://github.com/djangonauts/django-pgjson>`_
- `django-allauth <https://github.com/pennersr/django-allauth>`_
- `django-oauth-toolkit <https://github.com/evonove/django-oauth-toolkit>`_
- `django-model-utils <https://github.com/carljm/django-model-utils>`_
- `django-simple-history <https://github.com/treyhunner/django-simple-history>`_
- `django-aggregate-if <https://github.com/henriquebastos/django-aggregate-if>`_
- `django-youtube <https://github.com/laplacesdemon/django-youtube>`_
- `psycopg2 <http://initd.org/psycopg/>`_
- `iso8601 <https://bitbucket.org/micktwomey/pyiso8601>`_
- `pillow <http://python-pillow.github.io/>`_
- `django_nose <https://github.com/django-nose/django-nose>`_
- `pytz <http://pytz.sourceforge.net/>`_
- `gdata <https://code.google.com/p/gdata-python-client/>`_
- `easy-thumbnails <https://github.com/SmileyChris/easy-thumbnails>`_
- `moment <https://github.com/zachwill/moment>`_
- `requests <http://docs.python-requests.org/en/latest/>`_
- `factory-boy <http://factoryboy.readthedocs.org/en/latest/>`_
- `Handlebars <http://handlebarsjs.com>`_
- `Modernizr <https://modernizr.com>`_
- `Leaflet <http://leafletjs.com/>`_
- `Leaflet.Draw <https://github.com/Leaflet/Leaflet.draw>`_
- `jQuery <http://jquery.com/>`_
- `Bootstrap <http://getbootstrap.com/>`_
- `bootstrap-colorpicker <https://mjolnic.com/bootstrap-colorpicker/>`_
- `bootstrap-datetimepicker <https://eonasdan.github.io/bootstrap-datetimepicker/>`_
- `bootstrap-fileinput <https://github.com/kartik-v/bootstrap-fileinput>`_
