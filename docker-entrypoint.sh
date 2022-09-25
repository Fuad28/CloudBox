#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
#flask db init
#flask db migrate
#flask db upgrade

# Start server
echo "Starting server"
gunicorn -b  0.0.0.0:5000 cloudbox:app --workers=3
