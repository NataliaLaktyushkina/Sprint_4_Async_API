#!/bin/sh

echo "Waiting for Elasticsearch..."

#while ! nc -z $ES_HOST $ES_PORT; do
while ! nc -z elasticsearch 9200; do
  sleep 2
done

echo "Elasticsearch started"

exec "$@"