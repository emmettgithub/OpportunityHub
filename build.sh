#!/bin/bash

# Install system packages
apt-get update
apt-get install -y chromium chromium-driver

# Upgrade pip and install Python packages
pip install --upgrade pip
pip install -r requirements.txt
