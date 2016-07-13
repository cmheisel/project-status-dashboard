#!/bin/bash

set -euf -o pipefail

/app-ve/bin/python /app/manage.py migrate
/app-ve/bin/python /app/manage.py collectstatic --noinput

exec "$@"
