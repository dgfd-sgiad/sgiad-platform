#!/bin/bash

# ============================================================
# Script d'installation automatique - Plateforme DGFD Streamlit
# ============================================================

set -e  # Arrêt en cas d'erreur

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Affichage bannière
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  🚀 Installation automatique - Plateforme DGFD${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé. Veuillez l'installer :${NC}"
    echo -e "${YELLOW}   macOS : brew install python3${NC}"
    echo -e "${YELLOW}   Linux : sudo apt install python3 python3-pip${NC}"
    echo -e "${YELLOW}   Windows : https://python.org/downloads${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python détecté : $PYTHON_VERSION${NC}"

# Vérification de pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip3 non trouvé, tentative d'installation...${NC}"
    python3 -m ensurepip --upgrade || {
        echo -e "${RED}❌ Impossible d'installer pip. Merci de l'installer manuellement.${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✅ pip3 détecté${NC}"

# Chemin du dossier du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Création de l'environnement virtuel (optionnel)
read -p "$(echo -e ${YELLOW}🤔 Voulez-vous créer un environnement virtuel ? [o/N] : ${NC})" VENV_CHOICE
if [[ "$VENV_CHOICE" =~ ^[Oo]$ ]]; then
    echo -e "${BLUE}📦 Création de l'environnement virtuel...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
else
    echo -e "${YELLOW}⚠️  Installation en mode global (sans venv)${NC}"
fi

# Installation des dépendances
echo ""
echo -e "${BLUE}📥 Installation des dépendances...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo -e "${GREEN}✅ Dépendances installées avec succès${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt non trouvé, installation des dépendances principales...${NC}"
    pip3 install streamlit pandas plotly
    echo -e "${GREEN}✅ Dépendances de base installées${NC}"
fi

# Vérification de Streamlit
echo ""
echo -e "${BLUE}🔍 Vérification de Streamlit...${NC}"
if ! command -v streamlit &> /dev/null; then
    echo -e "${YELLOW}⚠️  Streamlit n'est pas dans le PATH, tentative d'installation...${NC}"
    pip3 install streamlit
fi

# Vérification que les fichiers essentiels existent
echo ""
echo -e "${BLUE}📁 Vérification des fichiers...${NC}"
if [ -f "dgfd_platform.py" ]; then
    echo -e "${GREEN}✅ dgfd_platform.py trouvé${NC}"
else
    echo -e "${RED}❌ dgfd_platform.py manquant !${NC}"
    exit 1
fi

if [ -f "data_manager.py" ]; then
    echo -e "${GREEN}✅ data_manager.py trouvé${NC}"
else
    echo -e "${RED}❌ data_manager.py manquant !${NC}"
    exit 1
fi

if [ -f "backup_manager.py" ]; then
    echo -e "${GREEN}✅ backup_manager.py trouvé (sauvegardes automatiques)${NC}"
else
    echo -e "${YELLOW}⚠️  backup_manager.py non trouvé${NC}"
fi

if [ -d "pages" ] && [ -f "pages/Admin.py" ]; then
    echo -e "${GREEN}✅ pages/Admin.py trouvé${NC}"
else
    echo -e "${YELLOW}⚠️  pages/Admin.py non trouvé${NC}"
fi

# Création des dossiers de données
if [ ! -d "data" ]; then
    mkdir -p data
    echo -e "${GREEN}✅ Dossier data créé${NC}"
fi

if [ ! -d "backups" ]; then
    mkdir -p backups
    echo -e "${GREEN}✅ Dossier backups créé (sauvegardes automatiques)${NC}"
fi

# ============================================================
# Lancement de l'application
# ============================================================
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}  🎉 Installation terminée avec succès !${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${BLUE}📋 Récapitulatif :${NC}"
echo -e "${GREEN}   • Page publique : streamlit run dgfd_platform.py${NC}"
echo -e "${GREEN}   • Admin : localhost:8501/pages/Admin${NC}"
echo -e "${GREEN}   • Backup auto : à chaque sauvegarde (rotation 10 fichiers)${NC}"
echo -e "${GREEN}   • Dossier backups : ./backups/${NC}"
echo -e "${GREEN}   • Admin login : admin / password${NC}"
echo ""

read -p "$(echo -e ${YELLOW}🚀 Lancer l'application maintenant ? [O/n] : ${NC})" LAUNCH_CHOICE
if [[ ! "$LAUNCH_CHOICE" =~ ^[Nn]$ ]]; then
    echo -e "${BLUE}🌐 Lancement de la plateforme DGFD...${NC}"
    echo -e "${YELLOW}   L'application s'ouvrira dans votre navigateur.${NC}"
    echo -e "${YELLOW}   Admin : login=admin / password=password${NC}"
    echo -e "${YELLOW}   Backups : crées automatiquement dans ./backups/${NC}"
    echo ""
    streamlit run dgfd_platform.py
else
    echo ""
    echo -e "${BLUE}💡 Pour lancer plus tard :${NC}"
    echo -e "${YELLOW}   cd $(basename $SCRIPT_DIR)${NC}"
    if [[ "$VENV_CHOICE" =~ ^[Oo]$ ]]; then
        echo -e "${YELLOW}   source venv/bin/activate${NC}"
    fi
    echo -e "${YELLOW}   streamlit run dgfd_platform.py${NC}"
    echo ""
    echo -e "${BLUE}💾 Pour créer une sauvegarde manuelle :${NC}"
    echo -e "${YELLOW}   python backup_manager.py --backup${NC}"
    echo -e "${YELLOW}   python backup_manager.py --list${NC}"
    echo ""
fi
