#!/bin/bash
# start_backend.sh — Start the backend server

cd /var/www/pakistanlawapp

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the server
python3 -m uvicorn server:app --host 0.0.0.0 --port 8020 --reload
