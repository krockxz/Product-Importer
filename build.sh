#!/usr/bin/env bash
# Build script for Render.com deployment

set -e  # Exit on any error

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies and build
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build process completed successfully!"