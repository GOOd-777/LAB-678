@echo off
cd /d %~dp0
color 0A
echo =====================================
echo   Motion Playground Web - Windows
 echo =====================================
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python не найден.
    echo Установите Python 3: https://www.python.org/downloads/windows/
    pause
    exit /b
)

echo.
echo Запуск локального сервера...
echo После запуска откройте:
echo http://localhost:8080
 echo.
python room_server.py
pause
