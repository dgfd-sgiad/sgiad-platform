@echo off
chcp 65001 >nul
title SGIAD - Configuration Pare-feu
color 0E

echo ============================================================
echo   SGIAD - Configuration du Pare-feu Windows
echo ============================================================
echo.
echo   Ce script ouvre le port 5000 dans le pare-feu Windows
echo   pour permettre aux collegues de se connecter au serveur.
echo.
echo   IMPORTANT: Ce script doit etre execute EN TANT
echo   QU'ADMINISTRATEUR (clic droit - Executer en tant
echo   qu'administrateur)
echo.
pause

REM Verifier les droits administrateur
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERREUR] Droits administrateur requis !
    echo Faites un clic droit sur ce fichier et choisissez
    echo "Executer en tant qu'administrateur"
    echo.
    pause
    exit /b 1
)

echo.
echo [1/2] Suppression d'une regle existante (si presente)...
netsh advfirewall firewall delete rule name="SGIAD Server Port 5000" >nul 2>&1

echo [2/2] Creation de la regle pare-feu...
netsh advfirewall firewall add rule name="SGIAD Server Port 5000" dir=in action=allow protocol=TCP localport=5000

if errorlevel 1 (
    echo.
    echo [ERREUR] Impossible de creer la regle pare-feu.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   [OK] Le port 5000 est maintenant ouvert !
echo.
echo   Vos collegues peuvent acceder a l'application via :
echo   http://<VOTRE_IP>:5000
echo.
echo   Pour trouver votre IP, ouvrez une invite de commande
echo   et tapez : ipconfig
echo ============================================================
echo.
pause
