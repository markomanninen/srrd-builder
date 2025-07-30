@echo off
setlocal enabledelayedexpansion
REM Windows Setup Script for SRRD-Builder MCP Server
REM Provides automated installation on Windows systems

REM Parse command line arguments
set RUN_TESTS=false
set WITH_VECTOR_DATABASE=false
set WITH_LATEX=false

set SRRD_LATEX_INSTALLED=false
set SRRD_VECTOR_DB_INSTALLED=false

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
        call :set_vector_db_success
    )
)
goto after_vector_db

:set_vector_db_success
set SRRD_VECTOR_DB_INSTALLED=true
goto :eof

:after_vector_db

REM Debug: Log start of LaTeX block
echo [DEBUG] Entering LaTeX install block >> setup_debug.log

REM --- Robust LaTeX (MiKTeX) install block ---
echo [DEBUG] Entering LaTeX install block >> setup_debug.log
if "%WITH_LATEX%"=="true" goto install_latex
goto continue_main

:install_latex
echo [DEBUG] WITH_LATEX true >> setup_debug.log
echo Installing LaTeX (MiKTeX)...
set MIKTEX_URL=https://miktex.org/download/win/basic-miktex-x64.exe
set MIKTEX_EXE=%TEMP%\basic-miktex-installer.exe
set RETRIES=3
set COUNT=0
if not exist "%MIKTEX_EXE%" goto download_miktex
echo [DEBUG] MiKTeX installer already exists >> setup_debug.log
goto run_miktex_installer

:download_miktex
echo [DEBUG] MiKTeX installer not found, downloading... >> setup_debug.log
echo Downloading MiKTeX installer...
:download_retry
powershell -Command "try { Invoke-WebRequest -Uri \"%MIKTEX_URL%\" -OutFile \"%MIKTEX_EXE%\" -ErrorAction Stop } catch { Write-Host 'Download failed:'; Write-Host $_.Exception.Message; exit 1 }"
set DL_EXIT=%errorlevel%
echo [DEBUG] Download exit code: %DL_EXIT% >> setup_debug.log
if %DL_EXIT% gtr 0 (
    set /a COUNT+=1
    echo [DEBUG] Download failed, attempt %COUNT% of %RETRIES% >> setup_debug.log
    if %COUNT% lss %RETRIES% (
        timeout /t 2 >nul
        goto download_retry
    ) else (
        echo [DEBUG] Download failed after %RETRIES% attempts >> setup_debug.log
        goto latex_fail
    )
)
echo [DEBUG] Download succeeded >> setup_debug.log

:run_miktex_installer
echo [DEBUG] Running MiKTeX installer >> setup_debug.log
echo Running installer: "%MIKTEX_EXE%" --unattended
"%MIKTEX_EXE%" --unattended
set INST_EXIT=%errorlevel%
echo [DEBUG] MiKTeX installer exit code: %INST_EXIT% >> setup_debug.log
if %INST_EXIT% gtr 0 (
    echo [DEBUG] MiKTeX installer failed >> setup_debug.log
    goto latex_fail
)
REM Check multiple possible MiKTeX installation paths
set "MIKTEX_PATHS=C:\Program Files\MiKTeX\miktex\bin\x64;C:\Program Files\MiKTeX\miktex\bin;C:\Program Files (x86)\MiKTeX\miktex\bin\x64;C:\Program Files (x86)\MiKTeX\miktex\bin;%USERPROFILE%\AppData\Local\Programs\MiKTeX\miktex\bin\x64;%USERPROFILE%\AppData\Local\Programs\MiKTeX\miktex\bin"

REM Add potential MiKTeX paths to PATH for testing
set "PATH=%PATH%;C:\Program Files\MiKTeX\miktex\bin\x64;C:\Program Files\MiKTeX\miktex\bin;C:\Program Files (x86)\MiKTeX\miktex\bin\x64;C:\Program Files (x86)\MiKTeX\miktex\bin"

where pdflatex >nul 2>&1
set PDFLATEX_FOUND=%errorlevel%
echo [DEBUG] where pdflatex errorlevel after PATH update: %PDFLATEX_FOUND% >> setup_debug.log

if %PDFLATEX_FOUND% equ 0 (
    echo LaTeX found in PATH after installation
    echo [DEBUG] pdflatex found in PATH, LaTeX installation successful >> setup_debug.log
    goto latex_success
)

REM Manual check of common MiKTeX installation locations
echo [DEBUG] pdflatex not in PATH, checking manual locations >> setup_debug.log

for %%p in ("C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" "C:\Program Files\MiKTeX\miktex\bin\pdflatex.exe" "C:\Program Files (x86)\MiKTeX\miktex\bin\x64\pdflatex.exe" "C:\Program Files (x86)\MiKTeX\miktex\bin\pdflatex.exe" "%USERPROFILE%\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe" "%USERPROFILE%\AppData\Local\Programs\MiKTeX\miktex\bin\pdflatex.exe") do (
    echo [DEBUG] Checking: %%p >> setup_debug.log
    if exist %%p (
        echo [DEBUG] Found pdflatex at %%p >> setup_debug.log
        echo LaTeX installed ^(found at %%p^)
        goto latex_success
    )
)

echo [DEBUG] No pdflatex found in any expected location >> setup_debug.log
goto latex_fail

:latex_success
set SRRD_LATEX_INSTALLED=true
echo [DEBUG] Variable set outside if block: SRRD_LATEX_INSTALLED=!SRRD_LATEX_INSTALLED! >> setup_debug.log
goto continue_main

echo [DEBUG] After LaTeX block, label check >> setup_debug.log

:latex_fail
echo [DEBUG] Entered :latex_fail label >> setup_debug.log
echo LaTeX installation failed - pdflatex not found in PATH
set SRRD_LATEX_INSTALLED=false
goto continue_main

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

REM Continue to main completion section



:continue_main
REM Debug: Show variable values before writing config
echo [DEBUG] SRRD_LATEX_INSTALLED before config: !SRRD_LATEX_INSTALLED! >> setup_debug.log
echo [DEBUG] SRRD_VECTOR_DB_INSTALLED before config: !SRRD_VECTOR_DB_INSTALLED! >> setup_debug.log

REM Save installation status to a config file
set INSTALL_CONFIG_DIR=srrd_builder\config
set INSTALL_CONFIG_FILE=!INSTALL_CONFIG_DIR!\installed_features.json

if not exist "!INSTALL_CONFIG_DIR!" mkdir "!INSTALL_CONFIG_DIR!"

(
echo {
echo   "latex_installed": !SRRD_LATEX_INSTALLED!,
echo   "vector_db_installed": !SRRD_VECTOR_DB_INSTALLED!
echo }
) > "!INSTALL_CONFIG_FILE!"

echo Installation status saved to !INSTALL_CONFIG_FILE!

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

echo Initializing global SRRD project context...


REM Automatically initialize SRRD project in the default project directory if not already initialized
set "DEFAULT_PROJECT_DIR=%USERPROFILE%\Projects\default"
if not exist "%DEFAULT_PROJECT_DIR%\.srrd" (
    echo.
    echo Initializing SRRD project in %DEFAULT_PROJECT_DIR% ...
    if not exist "%DEFAULT_PROJECT_DIR%" mkdir "%DEFAULT_PROJECT_DIR%"
    pushd "%DEFAULT_PROJECT_DIR%"
    srrd init || echo WARNING: 'srrd init' failed in %DEFAULT_PROJECT_DIR%. Please run it manually if needed.
    popd
) else (
    echo.
    echo SRRD project already initialized in %DEFAULT_PROJECT_DIR%.
)

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

echo Press any key to exit...
pause >nul