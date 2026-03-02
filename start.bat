@echo off
chcp 65001 >nul
title Seal Playerok Bot

cd /d "%~dp0"

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

:: Твой Python 3.12 (64-bit)
set "MY_PYTHON=C:\Users\Zion\AppData\Local\Programs\Python\Python312\python.exe"

:: Проверяем, есть ли файл
if not exist "%MY_PYTHON%" (
    echo.
    echo   ❌ Python не найден по пути: %MY_PYTHON%
    echo.
    pause
    exit /b 1
)

echo.
echo   ✅ Использую Python: %MY_PYTHON%
echo.

:: Показываем версию для проверки
"%MY_PYTHON%" --version
echo.

:: Запускаем бота
"%MY_PYTHON%" bot.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo   ============================================
    echo   ❌ Бот упал с ошибкой %ERRORLEVEL%
    echo   ============================================
    echo.
    echo   Окно закроется через 30 секунд...
    timeout /t 30
    exit /b 1
)

echo.
echo   ✅ Бот остановлен
pause