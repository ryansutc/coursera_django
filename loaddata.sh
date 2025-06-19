#!/bin/bash

# This script creates the simple sqlite example database and loads it with the fixture data.
python manage.py migrate --noinput
python manage.py loaddata ./fixtures/littlelemon_auth.json
python manage.py loaddata ./fixtures/littlelemon_api.json

print "database db.sqlite3 created and loaded with fixture data."