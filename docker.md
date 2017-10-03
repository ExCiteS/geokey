# GeoKey in containers

Download and install [Docker
CE](https://www.docker.com/community-edition#download) for your platform. This
will include the `docker-compose` command used below.

In one terminal run `docker-compose up --build` to pull and extract the
relevant images and build the GeoKey application container. In another
terminal, run
```
docker-compose exec geokey python manage.py migrate
```
to bring database tables up to date and
```
docker-compose exec geokey python manage.py collectstatic --noinput
```
to set up static files for serving. Now run the Django development server with
```
docker-compose exec geokey python manage.py runserver 0.0.0.0:8000
```

If everything went well, there should now be a GeoKey instance available on
your system at http://localhost:9000.

For development purposes, the source code is also mounted as a volume in the
`geokey` container, which means that changes made to the source code on the
host machine are reflected in the container.
