#!/bin/sh
echo "\n=== System Debug Info ==="
echo "Chromium version: $(chromium --version)"
echo "Chromedriver version: $(chromedriver --version)"
echo "Python version: $(python3 --version)"
echo "Current directory: $(pwd)"
echo "Environment variables:"
printenv 