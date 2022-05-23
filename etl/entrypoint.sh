#!/bin/sh
set -u

echo "Waiting for DB..."
#while ! nc -z $HOST $PORT; do
while ! nc -z postgres 5432; do
  sleep 2
done

echo "DB started"


echo "Waiting for Elasticsearch..."

#while ! nc -z $ES_HOST $ES_PORT; do
while ! nc -z elasticsearch 9200; do
  sleep 2
done

echo "Elasticsearch started"

exec "$@"