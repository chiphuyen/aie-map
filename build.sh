#!/usr/bin/env bash
# Build script for Render
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr

# Upgrade pip and setuptools first
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/uploads