@echo off
setlocal enabledelayedexpansion

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not found in PATH
    exit /b 1
)

:: Check Python version
for /f "tokens=2 delims=." %%I in ('python -c "import sys; print(sys.version.split()[0])"') do set PYTHON_VERSION=%%I
python -c "import sys; v=sys.version_info; exit(0 if v.major>=3 and v.minor>=9 else 1)"
if %ERRORLEVEL% neq 0 (
    echo Error: Python 3.9 or higher is required
    python --version
    exit /b 1
)

echo Checking system dependencies...
echo Python version:
python --version

:: Create and activate virtual environment
echo Creating virtual environment...
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip and install build dependencies
echo Installing build dependencies...
python -m pip install --upgrade pip
pip install build wheel setuptools_scm

:: Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.egg-info rmdir /s /q *.egg-info

:: Build the package
echo Building package...
python -m build

:: Verify the build
if exist dist (
    echo Build successful! The following files were created:
    dir /b dist
) else (
    echo Error: Build failed - no files were created in dist/
    exit /b 1
)

:: Run tests if pytest is available
where pytest >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Running tests...
    pytest
)

echo.
echo Build complete! To install the package:
echo.
echo 1. Install from wheel file:
echo    pip install dist\openhands_event_tracker-*.whl
echo.
echo 2. Or install in development mode:
echo    pip install -e .
echo.
echo To run the application:
echo 1. Start Kafka ^(if not using Docker^):
echo    docker-compose up -d kafka
echo.
echo 2. Run the application:
echo    event-tracker
echo.

:: Deactivate virtual environment
deactivate