#!/usr/bin/env bash
# Build script for Render
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr

# Set CARGO_HOME to a writable directory
export CARGO_HOME=/tmp/cargo
mkdir -p $CARGO_HOME

# Upgrade pip and setuptools first
pip install --upgrade pip setuptools wheel

# Install Python dependencies, preferring binary wheels
pip install --prefer-binary -r requirements.txt

# Create data directories
mkdir -p data/uploads