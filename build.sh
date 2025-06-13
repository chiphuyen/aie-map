#!/usr/bin/env bash
# Build script for Render
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr

# Install Python dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/uploads