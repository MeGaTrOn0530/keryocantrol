#!/bin/bash
# Production deployment script

echo "Starting Telegram Bot..."

# Create data directory
mkdir -p /app/data

# Set permissions
chmod 755 /app/data

# Start the application
python app.py
