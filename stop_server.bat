@echo off
echo Остановка серверов Python на порту 8080...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    taskkill /PID %%a /F >nul 2>nul
)
echo Готово.
pause
