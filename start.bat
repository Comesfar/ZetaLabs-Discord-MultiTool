@echo off
title ZetaLabs Discord Suite - Baslatiliyor...
chcp 65001 >nul
cd /d "%~dp0"

echo [1/3] Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi! Lutfen Python 3.10+ yukleyin ve PATH'e ekleyin: https://python.org
    pause
    exit /b 1
)

echo [2/3] Gereksinimler kontrol ediliyor...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo [3/3] ZetaLabs Suite baslatiliyor...
start "" pythonw main.pyw
exit
