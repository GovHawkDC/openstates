#!/bin/sh
set -e

echo "Scrape govhawk/openstates:2.0.1"

# copy use shift to get rid of first param, pass rest to pupa update
state=$1
shift

# Cheap n' dirty way to sync openstates patches and hotfixes; the idea
# here is that openstates gets updated more frequently w/ smaller
# changes than, e.g., pupa... so to avoid re-building the docker
# image...
#
# NOTE: noop the git pull call in case it fails
# @see https://stackoverflow.com/a/40650331/1858091
( cd /opt/openstates/openstates && \
  git stash && \
  ( git pull --no-edit origin govhawk-deploy || : ) )


export PYTHONPATH=./openstates

$PUPA_ENV/bin/pupa ${PUPA_ARGS:-} update $state "$@"
