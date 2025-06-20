#!/bin/bash
# Startup script for the Astrological API

echo "Starting Astrological API server..."

# Activate virtual environment if one is used (common practice)
# Adjust the path to your virtual environment if needed.
# For example, if your venv is in a folder named 'venv':
#
# if [ -d "venv" ]; then
#    echo "Activating virtual environment from ./venv..."
#    source venv/bin/activate
# elif [ -d ".venv" ]; then
#    echo "Activating virtual environment from ./.venv..."
#    source .venv/bin/activate
# else
#    echo "Virtual environment not found at ./venv or ./.venv. Assuming dependencies are globally installed or managed otherwise."
# fi

# Run Uvicorn server
# --reload will restart the server when code changes (useful for development)
# You might want to remove --reload for a production-like startup.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo "Server stopped."
