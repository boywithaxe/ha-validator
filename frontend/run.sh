#!/bin/bash

# Exit on error
set -e

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start dev server
echo "Starting frontend..."
npm run dev
