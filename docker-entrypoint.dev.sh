#!/bin/bash

# Apply database migrations
echo "Initiallizing and Apply database migrations"
flask db init
flask db migrate
flask db upgrade

# Start server
echo "Starting server"
flask run --host=0.0.0.0