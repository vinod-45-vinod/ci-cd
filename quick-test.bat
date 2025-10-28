@echo off
REM Quick Pipeline Test - Tests one service at a time
REM Usage: quick-test.bat [frontend|backend|python|all]

set SERVICE=%1

if "%SERVICE%"=="" (
    echo Usage: quick-test.bat [frontend^|backend^|python^|all]
    echo.
    echo Examples:
    echo   quick-test.bat frontend    - Test only frontend
    echo   quick-test.bat backend     - Test only backend
    echo   quick-test.bat python      - Test only Python service
    echo   quick-test.bat all         - Test all services
    exit /b 1
)

set "PROJECT_ROOT=%~dp0"

if /i "%SERVICE%"=="frontend" goto TEST_FRONTEND
if /i "%SERVICE%"=="backend" goto TEST_BACKEND
if /i "%SERVICE%"=="python" goto TEST_PYTHON
if /i "%SERVICE%"=="all" goto TEST_ALL

echo Invalid service: %SERVICE%
exit /b 1

:TEST_FRONTEND
echo Testing Frontend...
cd "%PROJECT_ROOT%frontend"
call npm install
call npm run test:coverage
call npm run lint
echo Frontend test complete!
goto END

:TEST_BACKEND
echo Testing Backend...
cd "%PROJECT_ROOT%backend"
call npm install
call npm run test:coverage
call npm run lint
echo Backend test complete!
goto END

:TEST_PYTHON
echo Testing Python Service...
cd "%PROJECT_ROOT%python_service"
pip install -r requirements.txt
playwright install chromium
pytest test_main_comprehensive.py --cov=main --cov-fail-under=75
pylint main.py --fail-under=7.5
bandit -r . -ll
echo Python test complete!
goto END

:TEST_ALL
echo Testing All Services...
call "%~f0" frontend
if errorlevel 1 exit /b 1
call "%~f0" backend
if errorlevel 1 exit /b 1
call "%~f0" python
if errorlevel 1 exit /b 1
echo.
echo ============================================================
echo ALL TESTS PASSED!
echo ============================================================
goto END

:END
echo.
pause
