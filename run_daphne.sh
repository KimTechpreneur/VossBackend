#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables
export DJANGO_SETTINGS_MODULE=VossBackend.settings
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run Daphne server
daphne -b 0.0.0.0 -p 8000 VossBackend.asgi:application 