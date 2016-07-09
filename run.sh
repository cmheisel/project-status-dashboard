#!/bin/bash

/app-ve/bin/python /app/manage.py migrate

exec "$@"
