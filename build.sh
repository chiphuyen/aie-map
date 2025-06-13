#!/usr/bin/env bash
# Build script for Render
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr python3-dev

# Set CARGO_HOME and other Rust env vars to writable locations
export CARGO_HOME=/tmp/.cargo
export RUSTUP_HOME=/tmp/.rustup
mkdir -p $CARGO_HOME $RUSTUP_HOME

# Upgrade pip and setuptools first
pip install --upgrade pip setuptools wheel

# Force installation of binary wheels only for problematic packages
pip install --only-binary :all: bcrypt

# Install remaining Python dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/uploads