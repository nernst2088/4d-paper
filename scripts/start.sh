#!/bin/bash
# Start 4D-Paper API Service

echo "==================================="
echo " Starting 4D-Paper API Server"
echo "==================================="

# Load environment variables
if [ -f .env ]; then
  export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

# Start uvicorn
uvicorn src.api.main:app \
  --host 0.0.0.0 \
  --port ${HTTP_PORT:-8000} \
  --reload