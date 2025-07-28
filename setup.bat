@echo off
setlocal enabledelayedexpansion
REM Windows Setup Script for SRRD-Builder MCP Server
REM Provides automated installation on Windows systems

REM Parse command line arguments
set RUN_TESTS=false
set WITH_VECTOR_DATABASE=false
set WITH_LATEX=false

:parse_args
if "%~1"=="" goto :args_done
if "%~1"=="--with-tests" (
    set RUN_TESTS=true
    shift
    goto :parse_args
)
if "%~1"=="--with-vector-database" (
    set WITH_VECTOR_DATABASE=true
    shift
    goto :parse_args
)
if "%~1"=="--with-latex" (
    set WITH_LATEX=true
    shift
    goto :parse_args
)
shift
goto :parse_args
:args_done

echo SRRD-Builder Windows Setup
echo ===============================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo Failed to activate virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment activation script not found
    echo Trying to recreate virtual environment...
    rmdir /s /q venv 2>nul
    python -m venv venv
    if errorlevel 1 (
        echo Failed to recreate virtual environment
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
)

REM Upgrade pip
echo Upgrading pip...
echo Using pip from: 
where pip
python -m pip install --upgrade pip --no-warn-script-location
if errorlevel 1 (
    echo Failed to upgrade pip
    pause
    exit /b 1
)

REM Clean previous installation
echo Cleaning previous SRRD-Builder installation...
pip uninstall -y srrd-builder >nul 2>&1
echo Previous installation cleaned

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Full requirements failed. Trying minimal installation...
    pip install -r requirements-minimal.txt
    if errorlevel 1 (
        echo Even minimal installation failed. Please check your Python environment.
        pause
        exit /b 1
    )
    echo Minimal dependencies installed
    echo Note: Some advanced features ^(semantic search, ML^) may not be available
) else (
    echo Python dependencies installed successfully
)

REM Install SRRD CLI package
echo Installing SRRD CLI package...
pip install -e .
if errorlevel 1 (
    echo SRRD CLI installation failed
    pause
    exit /b 1
)
echo SRRD CLI package installed successfully

REM Optional installations
if "%WITH_VECTOR_DATABASE%"=="true" (
    echo Installing vector database dependencies...
    pip install chromadb
    if errorlevel 1 (
        echo Vector database installation failed
    ) else (
        echo Vector database dependencies installed
        set SRRD_VECTOR_DB_INSTALLED=true
    )
)

if "%WITH_LATEX%"=="true" (
    echo Installing LaTeX...
    echo Please install MiKTeX manually from: https://miktex.org/download
    echo After installation, restart this script to continue.
    where pdflatex >nul 2>&1
    if errorlevel 1 (
        echo LaTeX installation failed - pdflatex not found in PATH
    ) else (
        echo LaTeX installed
        set SRRD_LATEX_INSTALLED=true
    )
)

REM Windows-specific setup
echo Setting up Windows-specific configurations...

REM Check for LaTeX installation
where pdflatex >nul 2>&1
if errorlevel 1 (
    echo LaTeX not found. Install MiKTeX for document generation:
    echo    https://miktex.org/download
    echo Document generation tools will show helpful error messages without LaTeX
) else (
    echo LaTeX found
)

REM Test basic functionality
echo Testing basic functionality...
python -c "import srrd_builder; print('Package import successful')"
if errorlevel 1 (
    echo Package import failed
    pause
    exit /b 1
)

REM Test CLI command
echo Testing CLI command...
python -m srrd_builder.cli.main --version
if errorlevel 1 (
    echo CLI test failed
    pause
    exit /b 1
)

REM Test pytest
python -m pytest --version >nul 2>&1
if errorlevel 1 (
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
REM Optional test suite execution
if "%RUN_TESTS%"=="true" (
    echo.
    echo Running Professional Test Suite ^(158 tests^)...
    echo =================================================
    
    if exist "run_tests.sh" (
        bash run_tests.sh
        if errorlevel 1 (
            echo Some tests failed. Check test output above.
            echo Installation is still functional - tests validate code quality.
        ) else (
            echo All 158 tests passed successfully!
        )
    ) else (
        echo Test runner not found. Skipping test execution.
    )
) else (
    echo.
    echo To run the professional test suite ^(158 tests^):
    echo    bash run_tests.sh
    echo    or
    echo    setup.bat --with-tests
)

REM Save installation status to a config file
set INSTALL_CONFIG_DIR=srrd_builder\config
set INSTALL_CONFIG_FILE=%INSTALL_CONFIG_DIR%\installed_features.json

if not exist "%INSTALL_CONFIG_DIR%" mkdir "%INSTALL_CONFIG_DIR%"

echo { > "%INSTALL_CONFIG_FILE%"
echo   "latex_installed": %SRRD_LATEX_INSTALLED:true=true%, >> "%INSTALL_CONFIG_FILE%"
echo   "vector_db_installed": %SRRD_VECTOR_DB_INSTALLED:true=true% >> "%INSTALL_CONFIG_FILE%"
echo } >> "%INSTALL_CONFIG_FILE%"

echo Installation status saved to %INSTALL_CONFIG_FILE%

echo.
echo Initializing global SRRD project context...
python -c "import sys; sys.path.insert(0, r'%cd%\srrd_builder\utils'); import launcher_config; launcher_config.reset_to_global_project()"
echo Global SRRD project context initialized (if not already present)
pause >nul