#!/bin/bash

# Ensure pyinstaller is installed
pip install pyinstaller

# Create the executable with pyinstaller and add the icon
pyinstaller --onefile --windowed --name vhf_uhf_propagation_tool src/main.py

echo "Executable created successfully."