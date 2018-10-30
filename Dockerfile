FROM ecarrara/python-gdal

RUN apt-get update && apt-get install -y libmagickcore-dev libmagickwand-dev imagemagick libav-tools nodejs npm
RUN sed -i 's/\(<policy domain="coder" rights=\)"none" \(pattern="PDF" \/>\)/\1"read|write"\2/g' /etc/ImageMagick-6/policy.xml
RUN ln -s /usr/bin/nodejs /usr/bin/node

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

ADD /geokey/local_settings /app/local_settings
ADD /geokey /app

WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
RUN pip install -e /app
RUN npm install
