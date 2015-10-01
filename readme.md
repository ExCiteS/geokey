# GeoKey

[![Build Status](https://travis-ci.org/ExCiteS/geokey.svg?branch=master)](https://travis-ci.org/ExCiteS/geokey) [![Coverage Status](https://coveralls.io/repos/ExCiteS/geokey/badge.png)](https://coveralls.io/r/ExCiteS/geokey) [![Requirements Status](https://requires.io/github/ExCiteS/geokey/requirements.svg?branch=master)](https://requires.io/github/ExCiteS/geokey/requirements/?branch=master) [![Code Health](https://landscape.io/github/ExCiteS/geokey/master/landscape.svg?style=plastic)](https://landscape.io/github/ExCiteS/geokey/master)

GeoKey is a platform for participatory mapping that is currently developed at [Extreme Citizen Science Research Group](http://ucl.ac.uk/excites) at University College London.

## Developing

### Install for development

#### Installing pre-requisites

1. Update your system

    ```
    sudo apt-get update && sudo apt-get upgrade
    ```

2. Install Postgres and PostGIS (we follow the [official guides](http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS21UbuntuPGSQL93Apt))

    ```
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt wheezy-pgdg main" >> /etc/apt/sources.list'
    wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update

    sudo apt-get install postgresql-9.4-postgis-2.1 postgresql-contrib postgresql-server-dev-9.4
    ```

3. Setup all other dependencies

    ```
    sudo apt-get install python-pip python-virtualenv python-dev libjpeg-dev
    ```

#### Setup the database

1. For simplicity, switch to user postgres:

    ```
    sudo su - postgres
    ```

2. Install postgis in template1 (only required for running tests):

    ```
    psql -d template1 -c 'create extension hstore;'
    ```

3. Log in to the database

    ```
    psql
    ```

4. Create the user

    ```
    postgres=# CREATE USER django WITH PASSWORD 'django123';
    ```

5. Make _django_ super user on your data base (this is required for tests only and shouldn't be done in production):

    ```
    postgres=# ALTER ROLE django WITH superuser;
    ```

6. Create the database

    ```
    postgres=# CREATE DATABASE geokey OWNER django;
    ```
    
7. Log out and connect to database geokey:

    ```
    postgres=# \q
    $ psql -d geokey
    ```

8. Install the extensions on database geokey

    ```
    geokey=# CREATE EXTENSION postgis;
    geokey=# CREATE EXTENSION hstore;
    ```
    
9. Logout of database geokey and logout user postgres

    ```
    geokey=# \q
    $ logout
    ```


#### Setting up GeoKey

1. Clone the repository (you should use your own fork)

    ```
    git clone https://github.com/ExCiteS/geokey.git
    ```

2. Install the package and development requirements

    ```
    cd geokey
    pip install -e .
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```
    
    You may need to add `sudo ` before the `pip` commands if you are not logged in as root or working within a virtual environment.

3. Copy the directory `local_settings.example` to `local_settings`

  ```
  cp -r local_settings.example local_settings
  ```

4. Inside `local_settings` open `settings.py` in a text editor and add your database settings:

  ```
  DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'geokey',
            'USER': 'django',
            'PASSWORD': 'django123',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

    SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  ```

5. Migrate the database

    ```
    python manage.py migrate
    ```

6. Add yourself as super user. You can use the same email and password to log into the system later.

    ```
    python manage.py createsuperuser
    ```

### Run the test server

```
python manage.py runserver 0.0.0.0:8000
```

### Run tests

```
python manage.py test
```

## We use open-source technologies

GeoKey was built using some amazing open-source technology. We would like to thank all contributors to these projects:

- [Django](https://www.djangoproject.com/)
- [django-hstore](https://github.com/djangonauts/django-hstore)
- [psycopg2](http://initd.org/psycopg/)
- [iso8601](https://bitbucket.org/micktwomey/pyiso8601)
- [django-oauth-toolkit](https://github.com/evonove/django-oauth-toolkit)
- [django-model-utils](https://github.com/carljm/django-model-utils)
- [djangorestframework](http://www.django-rest-framework.org/)
- [djangorestframework-gis](https://github.com/djangonauts/django-rest-framework-gis)
- [django-simple-history](https://github.com/treyhunner/django-simple-history)
- [django-aggregate-if](https://github.com/henriquebastos/django-aggregate-if)
- [django_braces](https://github.com/brack3t/django-braces)
- [pillow](http://python-pillow.github.io/)
- [django_nose](https://github.com/django-nose/django-nose)
- [factory-boy](http://factoryboy.readthedocs.org/en/latest/)
- [pytz](http://pytz.sourceforge.net/)
- [django-youtube](https://github.com/laplacesdemon/django-youtube)
- [gdata](https://code.google.com/p/gdata-python-client/)
- [easy-thumbnails](https://github.com/SmileyChris/easy-thumbnails)
- [requests](http://docs.python-requests.org/en/latest/)
- [Leaflet](http://leafletjs.com/)
- [Leaflet Draw](https://github.com/Leaflet/Leaflet.draw)
- [jQuery](http://jquery.com/)
- [Bootstrap](http://getbootstrap.com/)
