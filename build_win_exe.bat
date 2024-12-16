@echo off

:: Ensure pyinstaller is installed
pip install pyinstaller

:: Create the executable with pyinstaller and add the icon
pyinstaller --onefile --windowed --icon=res\icon.png --name vhf_uhf_propagation_tool src\main.py

echo Executable created successfully.
pause