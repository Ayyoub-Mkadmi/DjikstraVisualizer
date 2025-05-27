@echo off
REM Batch file to install Python dependencies for Dijkstra Visualizer Project
title Installing Dependencies for Dijkstra Visualizer
color 0A

echo ********************************************
echo * Installing Required Python Packages      *
echo ********************************************
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b
)

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with your Python installation
    pause
    exit /b
)

echo Installing PyQt5...
python -m pip install PyQt5 --user

echo Installing NetworkX...
python -m pip install networkx --user

echo Installing Matplotlib...
python -m pip install matplotlib --user

echo.
echo ********************************************
echo * All Dependencies Successfully Installed! *
echo ********************************************
echo.
echo You can now run the application with: python run.py
pause