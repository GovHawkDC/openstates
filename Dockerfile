FROM  alpine:3.9
LABEL maintainer="James Turk <james@openstates.org>"

ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'en_US.UTF-8'
ENV PUPA_ENV /opt/openstates/venv-pupa/

ADD . /opt/openstates/openstates

RUN apk add --no-cache --virtual .build-dependencies \
    wget \
    build-base \
    autoconf \
    automake \
    libtool && \
  apk add --no-cache \
    git \
    curl \
    unzip \
    gcc \
    glib \
    glib-dev \
    libressl-dev \
    libffi-dev \
    freetds-dev \
    python3 \
    python3-dev \
    py-virtualenv \
    libxml2-dev \
    libxslt-dev \
    yaml-dev \
    poppler-utils \
    postgresql-dev \
    postgresql-client \
    mariadb \
    mariadb-dev \
    mariadb-client && \
  apk add --no-cache \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    libcrypto1.1 && \
  apk add --no-cache \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    gdal-dev \
    geos-dev && \
  pip3 install awscli && \
  cd /tmp && \
    wget "https://github.com/brianb/mdbtools/archive/0.7.1.zip" && \
    unzip 0.7.1.zip && rm 0.7.1.zip && \
    cd mdbtools-0.7.1 && \
    autoreconf -i -f && \
    ./configure --disable-man && make && make install && \
    cd /tmp && \
    rm -rf mdbtools-0.7.1 && \
  virtualenv -p $(which python3) /opt/openstates/venv-pupa/ && \
    /opt/openstates/venv-pupa/bin/pip install -e git+https://github.com/opencivicdata/python-opencivicdata-django.git#egg=opencivicdata && \
    /opt/openstates/venv-pupa/bin/pip install -e git+https://github.com/GovHawkDC/pupa.git@feature/inline-cache-check#egg=pupa && \
    /opt/openstates/venv-pupa/bin/pip install -r /opt/openstates/openstates/requirements.txt && \
  apk del .build-dependencies

RUN git config --global user.email "user@example.org"
RUN git config --global user.name "Example User"
RUN git config --global core.mergeoptions --no-edit

WORKDIR /opt/openstates/openstates/
RUN git remote set-url origin https://github.com/GovHawkDC/openstates.git
ENTRYPOINT ["/opt/openstates/openstates/pupa-scrape.sh"]
