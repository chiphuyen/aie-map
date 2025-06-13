#!/usr/bin/env bash
# Build script for Render
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr libffi-dev

# Set environment variables to avoid Rust compilation
export CRYPTOGRAPHY_DONT_BUILD_RUST=1

# Upgrade pip and setuptools first
pip install --upgrade pip setuptools wheel

# Install cryptography and bcrypt from pre-built wheels
pip install --only-binary :all: cryptography bcrypt

# Install Python dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/uploads