FROM ubuntu:14.04

RUN apt-get update && \
    apt-get install -y \
        binutils \
        g++ \
        libav-tools \
        python \
        libpython-dev \
        libgdal-dev \
        imagemagick \
        libmagickcore-dev \
        libmagickwand-dev \
        curl \
        wget && \
    apt-get clean

RUN sed -i 's/\(<policy domain="coder" rights=\)"none" \(pattern="PDF" \/>\)/\1"read|write"\2/g' /etc/ImageMagick/policy.xml

RUN python --version
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" && \
    python get-pip.py && \
    rm get-pip.py && \
    pip --version

RUN gdal-config --version && \
    export C_INCLUDE_PATH=/usr/include/gdal && \
    export CPLUS_INCLUDE_PATH=/usr/include/gdal && \
    pip install gdal==1.10

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get install -y nodejs && \
    node -v &&  npm -v

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz && \
    tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz && \
    rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

ADD /geokey /app

WORKDIR /app
RUN \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt && \
    pip install -e /app
RUN npm install
