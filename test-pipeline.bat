@echo off
REM CI/CD Pipeline Local Test Script
REM Run this to test all services before pushing to GitHub

echo.
echo ============================================================
echo       CI/CD Pipeline - Local Testing Script
echo ============================================================
echo.

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo Current directory: %CD%
echo.

REM Color output (for Windows 10+)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "NC=[0m"

echo.
echo ============================================================
echo STEP 1: Testing Frontend
echo ============================================================
echo.

cd "%PROJECT_ROOT%frontend"
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo %RED%Frontend dependency installation failed!%NC%
        pause
        exit /b 1
    )
)

echo.
echo Running frontend tests with coverage...
call npm run test:coverage
if errorlevel 1 (
    echo %RED%Frontend tests FAILED!%NC%
    echo Check the output above for details.
    pause
    exit /b 1
)

echo.
echo Running frontend linting...
call npm run lint
if errorlevel 1 (
    echo %RED%Frontend linting FAILED!%NC%
    echo Try running: npm run lint:fix
    pause
    exit /b 1
)

echo.
echo %GREEN%✓ Frontend tests PASSED!%NC%
echo.

echo ============================================================
echo STEP 2: Testing Backend
echo ============================================================
echo.

cd "%PROJECT_ROOT%backend"
if not exist "node_modules" (
    echo Installing backend dependencies...
    call npm install
    if errorlevel 1 (
        echo %RED%Backend dependency installation failed!%NC%
        pause
        exit /b 1
    )
)

echo.
echo Running backend tests with coverage...
call npm run test:coverage
if errorlevel 1 (
    echo %RED%Backend tests FAILED!%NC%
    echo Check the output above for details.
    pause
    exit /b 1
)

echo.
echo Running backend linting...
call npm run lint
if errorlevel 1 (
    echo %RED%Backend linting FAILED!%NC%
    echo Try running: npm run lint:fix
    pause
    exit /b 1
)

echo.
echo %GREEN%✓ Backend tests PASSED!%NC%
echo.

echo ============================================================
echo STEP 3: Testing Python Service
echo ============================================================
echo.

cd "%PROJECT_ROOT%python_service"

echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo %RED%Python dependency installation failed!%NC%
    pause
    exit /b 1
)

echo.
echo Installing Playwright browser...
playwright install chromium
if errorlevel 1 (
    echo %YELLOW%Warning: Playwright installation had issues%NC%
    echo This might be OK if Chromium is already installed
)

echo.
echo Running Python tests with coverage...
pytest test_main_comprehensive.py --cov=main --cov-report=term --cov-fail-under=75
if errorlevel 1 (
    echo %RED%Python tests FAILED!%NC%
    echo Check the output above for details.
    pause
    exit /b 1
)

echo.
echo Running pylint (must score >=7.5/10)...
pylint main.py --fail-under=7.5
if errorlevel 1 (
    echo %RED%Pylint score too low!%NC%
    echo Review the output above and fix issues.
    pause
    exit /b 1
)

echo.
echo Running bandit security scan...
bandit -r . -ll
if errorlevel 1 (
    echo %YELLOW%Warning: Bandit found security issues%NC%
    echo Review the output above.
)

echo.
echo %GREEN%✓ Python tests PASSED!%NC%
echo.

echo ============================================================
echo                    ALL TESTS PASSED!
echo ============================================================
echo.
echo %GREEN%✓ Frontend: Tests, Coverage (>=75%%), Lint - PASSED%NC%
echo %GREEN%✓ Backend:  Tests, Coverage (>=75%%), Lint - PASSED%NC%
echo %GREEN%✓ Python:   Tests, Coverage (>=75%%), Pylint (>=7.5) - PASSED%NC%
echo.
echo ============================================================
echo You are ready to push to GitHub!
echo ============================================================
echo.
echo Next steps:
echo 1. git add .
echo 2. git commit -m "feat: Complete CI/CD pipeline"
echo 3. git push origin main
echo 4. Go to GitHub Actions to watch pipeline execute
echo.
echo Coverage reports are available at:
echo - Frontend: %PROJECT_ROOT%frontend\coverage\lcov-report\index.html
echo - Backend:  %PROJECT_ROOT%backend\coverage\lcov-report\index.html
echo - Python:   %PROJECT_ROOT%python_service\htmlcov\index.html
echo.

pause
