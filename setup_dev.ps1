# setup_dev.ps1
# Script d'assistance pour préparer un environnement de développement local.

$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectPath

Write-Host "[1/3] Installation des dépendances..." -ForegroundColor Cyan
pip install -r requirements.txt

if (-Not (Test-Path .env)) {
    Write-Host "[2/3] Copie du fichier .env.example vers .env..." -ForegroundColor Cyan
    Copy-Item .env.example .env
    Write-Host "   -> Fichier .env créé. Pense à le modifier avec tes clés Supabase." -ForegroundColor Yellow
} else {
    Write-Host "[2/3] Le fichier .env existe déjà. Vérifie qu'il contient SUPABASE_URL et SUPABASE_KEY." -ForegroundColor Green
}

Write-Host "[3/3] Environnement prêt. Lance le serveur avec : python api.py" -ForegroundColor Green
