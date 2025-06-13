#!/usr/bin/env bash
# Build script for Render
set -o errexit

# Show Python version for debugging
echo "Python version:"
python --version
echo "Pip version:"
pip --version

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr

# Upgrade pip to ensure we get the latest wheel support
python -m pip install --upgrade pip setuptools wheel

# Install all dependencies, preferring binary wheels
# Use --prefer-binary to avoid building from source
pip install --prefer-binary -r requirements.txt

# Create data directories
mkdir -p data/uploads