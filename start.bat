@echo off
title MuhasebeDiyari - Dukkan Muhasebe Uygulamasi
echo ==========================================
echo   MuhasebeDiyari - Dukkan Muhasebe App
echo ==========================================
echo.

cd /d "%~dp0"

:: Check/create virtual environment
echo [1/4] Sanal ortam kontrol ediliyor...
if not exist "venv\Scripts\activate.bat" (
    echo        Venv bulunamadi, olusturuluyor...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo HATA: Sanal ortam olusturulamadi. Python 3.10+ yuklu oldugundan emin olun.
        pause
        exit /b 1
    )
    echo        Venv olusturuldu.
)
call venv\Scripts\activate.bat
echo        Venv aktif.

:: Install requirements inside venv
echo [2/4] Python paketleri kontrol ediliyor...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo HATA: Paketler yuklenemedi! Lutfen manuel olarak calistirin:
    echo        venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)
echo        Paketler hazir.

:: Start the application
echo [3/4] Uygulama baslatiliyor (Port: 5050)...
start python run.py
timeout /t 3 /nobreak >nul

:: Seed admin user silently
echo [4/4] Admin kullanicisi olusturuluyor...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5050/seed-admin' -UseBasicParsing -TimeoutSec 10; Write-Host $r.Content } catch { Write-Host 'Admin zaten mevcut veya uygulama henuz hazir degil.' }" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ==========================================
echo   Basariyla baslatildi!
echo   Tarayici acilacak: http://127.0.0.1:5050
echo.
echo ==========================================
echo.

start http://127.0.0.1:5050

echo Uygulama calisiyor... Kapatmak icin bu pencereyi kapatin.
pause >nul
