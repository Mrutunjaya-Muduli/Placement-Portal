#!/bin/bash
# Install dependencies
python3 -m pip install --break-system-packages -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput --clear

# Run migrations
python3 manage.py migrate --noinput

# Seed mock data
python3 manage.py seed_data
