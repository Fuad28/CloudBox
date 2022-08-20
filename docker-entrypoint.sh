#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
flask db upgrade
flask db upgrade

# Start server
echo "Starting server"
gunicorn -b  0.0.0.0:5000 prod-run:app --workers=3