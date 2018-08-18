FROM python:2.7

RUN apt-get update && apt-get install -y wget

ENV DOCKERIZE_VERSION v0.5.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN apt-get install -y libgdal-dev
RUN pip install --global-option=build_ext --global-option="-I/usr/include/gdal" gdal==1.10

ADD /geokey/local_settings /app/local_settings
ADD /geokey /app

WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
RUN pip install -e /app
