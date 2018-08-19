FROM ecarrara/python-gdal

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

ADD /geokey/local_settings /app/local_settings
ADD /geokey /app
# Uncomment for communitymaps.
# ADD /geokey-communitymaps /extensions/geokey-communitymaps

WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
RUN pip install -e /app
# Uncomment for communitymaps.
# RUN pip install -e /extensions/geokey-communitymaps
