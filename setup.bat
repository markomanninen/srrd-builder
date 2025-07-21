@echo off
setlocal enabledelayedexpansion
REM Windows Setup Script for SRRD-Builder MCP Server
REM Provides automated installation on Windows systems

echo SRRD-Builder Windows Setup
echo ===============================

REM Check Python installation
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo Full requirements failed. Trying minimal installation...
    pip install -r requirements-minimal.txt
    if !errorlevel! neq 0 (
        echo Even minimal installation failed. Please check your Python environment.
        pause
        exit /b 1
    )
    echo Minimal dependencies installed
    echo Note: Some advanced features (semantic search, ML) may not be available
) else (
    echo Python dependencies installed successfully
)

REM Install SRRD CLI package
echo Installing SRRD CLI package...
pip install -e .
if !errorlevel! neq 0 (
    echo SRRD CLI installation failed
    pause
    exit /b 1
)
echo SRRD CLI package installed successfully

REM Windows-specific setup
echo Setting up Windows-specific configurations...

REM Check for LaTeX installation
where pdflatex >nul 2>&1
if !errorlevel! neq 0 (
    echo LaTeX not found. Install MiKTeX for document generation:
    echo    https://miktex.org/download
    echo Document generation tools will show helpful error messages without LaTeX
) else (
    echo LaTeX found
)

REM Test basic functionality
echo Testing basic functionality...
python -c "import srrd_builder; print('Package import successful')"
if !errorlevel! neq 0 (
    echo Package import failed
    pause
    exit /b 1
)

REM Test CLI command
echo Testing CLI command...
python -m srrd_builder.cli.main --version
if !errorlevel! neq 0 (
    echo CLI test failed
    pause
    exit /b 1
)

REM Test pytest
python -m pytest --version >nul 2>&1
if !errorlevel! neq 0 (
    echo Pytest not working correctly
    pause
    exit /b 1
)
echo Pytest configured correctly

echo.
echo SRRD-Builder installation complete!
echo.
echo Next steps:
echo    1. Initialize a project: srrd init
echo    2. Configure Claude Desktop: srrd configure --claude
echo    3. Check status: srrd configure --status
echo.
echo Available commands:
echo    - srrd init           Initialize new research project
echo    - srrd switch         Switch MCP context to current project
echo    - srrd configure      Configure and check status
echo    - srrd-server         Start WebSocket demo server
echo.
echo Press any key to exit...
pause >nul