@echo off
chcp 65001 >nul
title SGIAD - Serveur de la Plateforme Nationale
color 0A

echo ============================================================
echo   SGIAD - Serveur de la Plateforme Nationale
echo ============================================================
echo.

REM Verifier que Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe !
    echo Installez Python 3.10+ depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verifier les dependances
echo [1/2] Verification des dependances...
pip install -r requirements.txt --quiet 2>nul

REM Obtenir l'IP locale
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set IP_ADDRESS=%%b
    )
)

echo.
echo ============================================================
echo   [2/2] Demarrage du serveur...
echo ============================================================
echo.
echo   Acces LOCAL   : http://127.0.0.1:5000
echo   Acces RESEAU  : http://%IP_ADDRESS%:5000
echo.
echo   Partagez cette URL avec vos collegues :
echo   ^>^>^> http://%IP_ADDRESS%:5000 ^<^<^<
echo.
echo   Appuyez sur Ctrl+C pour arreter le serveur
echo ============================================================
echo.

REM Lancer le serveur Flask
python api.py

pause
