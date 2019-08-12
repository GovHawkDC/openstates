#!/bin/sh

set -e

# copy use shift to get rid of first param, pass rest to pupa update
state=$1
shift

# The gentleman's delivery/deployment hehe
#
# NOTE: noop the git pull call in case it fails
# @see https://stackoverflow.com/a/40650331/1858091
( cd /opt/openstates/openstates && \
  git stash && \
  ( git pull origin govhawk-deploy || : ) )


export PYTHONPATH=./openstates

$PUPA_ENV/bin/pupa ${PUPA_ARGS:-} update $state "$@"
