#!/bin/bash

set -euf -o pipefail

echo "DEBUG: $DEBUG"

if [[ "$DEBUG" = "True" ]]; then
  echo "Starting runserver."
  /app-ve/bin/python /app/manage.py runserver 0.0.0.0:8000
else
  echo "Starting gunicorn."
  exec /app-ve/bin/gunicorn projects.wsgi:application \
      --name dashboard \
      --bind 0.0.0.0:8000 \
      --workers 3 \
      --log-level=info
fi
