FROM        ubuntu:artful
MAINTAINER  James Turk <james@openstates.org>

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python2.7 \
    python-pip \
    python-lxml \
    libssl-dev \
    mdbtools \
    python-dev \
    python3-dev \
    poppler-utils \
    python-virtualenv \
    python3.5 \
    git \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    gdal-bin \
    s3cmd \
    freetds-dev \
    curl \
    wget \
    unzip \
    mysql-server \
    libmysqlclient-dev \
    postgresql-client-9.6 \
    gnupg \
    dirmngr

# add mongo 3.4 packages
RUN echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" > /etc/apt/sources.list.d/mongodb-org-3.4.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
RUN apt-get update && apt-get install -y mongodb-org-tools


RUN mkdir -p /opt/openstates/
RUN mkdir -p /var/run/mysqld/
RUN chown mysql /var/run/mysqld/

RUN virtualenv -p $(which python2) /opt/openstates/venv-billy/
RUN /opt/openstates/venv-billy/bin/pip install -e git+https://github.com/openstates/billy.git#egg=billy
RUN /opt/openstates/venv-billy/bin/pip install -U python-dateutil requests

RUN virtualenv -p $(which python3) /opt/openstates/venv-pupa/
RUN /opt/openstates/venv-pupa/bin/pip install -e git+https://github.com/opencivicdata/python-opencivicdata.git#egg=python-opencivicdata
RUN /opt/openstates/venv-pupa/bin/pip install -e git+https://github.com/GovHawkDC/pupa.git@feature/always-s3#egg=pupa

ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'en_US.UTF-8'
ENV BILLY_ENV /opt/openstates/venv-billy/
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
    glib \
    glib-dev \
    libressl-dev \
    libffi-dev \
    freetds-dev \
    python \
    python-dev \
    python3 \
    python3-dev \
    py-virtualenv \
    libxml2-dev \
    libxslt-dev \
    poppler-utils \
    postgresql-dev \
    mariadb-dev && \
  apk add --no-cache \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    libressl2.7-libcrypto && \
  apk add --no-cache \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    gdal-dev \
    geos-dev && \
  cd /tmp && \
    wget "https://github.com/brianb/mdbtools/archive/0.7.1.zip" && \
    unzip 0.7.1.zip && rm 0.7.1.zip && \
    cd mdbtools-0.7.1 && \
    autoreconf -i -f && \
    ./configure --disable-man && make && make install && \
    cd /tmp && \
    rm -rf mdbtools-0.7.1 && \
  virtualenv -p $(which python2) /opt/openstates/venv-billy/ && \
    /opt/openstates/venv-billy/bin/pip install -e git+https://github.com/openstates/billy.git#egg=billy && \
    /opt/openstates/venv-billy/bin/pip install python-dateutil && \
  virtualenv -p $(which python3) /opt/openstates/venv-pupa/ && \
    /opt/openstates/venv-pupa/bin/pip install -e git+https://github.com/opencivicdata/python-opencivicdata-django.git#egg=python-opencivicdata && \
    /opt/openstates/venv-pupa/bin/pip install -e git+https://github.com/opencivicdata/pupa.git#egg=pupa && \
    /opt/openstates/venv-pupa/bin/pip install -r /opt/openstates/openstates/requirements.txt && \
  apk del .build-dependencies

# Adding these so we can git pull in pupa-scrape.sh...
RUN git config --global user.email "user@example.org"
RUN git config --global user.name "Example User"
RUN git config --global core.mergeoptions --no-edit

WORKDIR /opt/openstates/openstates/
RUN git remote set-url origin https://github.com/GovHawkDC/openstates.git
ENTRYPOINT ["/opt/openstates/openstates/pupa-scrape.sh"]