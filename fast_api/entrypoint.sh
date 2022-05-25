#!/bin/sh

echo "Waiting for Elasticsearch..."

#while ! nc -z $ES_HOST $ES_PORT; do
while ! nc -z elasticsearch 9200; do
  sleep 2
done

echo "Elasticsearch started"

gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8100 main:app

