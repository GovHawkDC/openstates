FROM ubuntu:bionic
LABEL maintainer="GovHawk, LLC"

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONIOENCODING "utf-8"
ENV LANG "en_US.UTF-8"
ENV LANGUAGE=en_US:en
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PUPA_ENV /opt/openstates/venv-pupa/

ADD . /opt/openstates/openstates

RUN apt-get update

# Deps: Utils
RUN apt-get install -y \
        curl \
        dirmngr \
        gcc \
        git \
        gnupg \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        poppler-utils \
        s3cmd \
        unzip \
        wget

# Deps: Python3
RUN apt-get install -y \
        python-virtualenv \
        python3 \
        python3-dev \
        python3-pip

# Deps: Databases
RUN apt-get install -y \
        mysql-client

# Deps: Geo
RUN apt-get install -y \
        libgeos-dev \
        libgdal-dev \
        gdal-bin

# Deps: Microsoft handling
RUN apt-get install -y \
        mdbtools \
        freetds-dev

RUN virtualenv -p $(which python3) /opt/openstates/venv-pupa/
RUN /opt/openstates/venv-pupa/bin/pip install -e git+https://github.com/GovHawkDC/pupa.git@feature/inline-cache-check#egg=pupa
RUN /opt/openstates/venv-pupa/bin/pip install -r /opt/openstates/openstates/requirements.txt

WORKDIR /opt/openstates/openstates/

RUN git config --global user.email "user@example.org"
RUN git config --global user.name "Example User"
RUN git config --global core.mergeoptions --no-edit
RUN git remote set-url origin https://github.com/GovHawkDC/openstates.git

ENTRYPOINT ["/opt/openstates/openstates/pupa-scrape.sh"]
