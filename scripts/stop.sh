#!/bin/bash
# Stop 4D-Paper API

pkill -f "uvicorn src.api.main:app"
echo "4D-Paper API stopped."