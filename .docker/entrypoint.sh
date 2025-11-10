#!/bin/bash
set -e

# Activate venv
source /home/appuser/app/venv/bin/activate

python -m uvicorn --host 0.0.0.0 --port 8000 --reload skeleton.asgi:application