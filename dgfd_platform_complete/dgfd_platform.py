import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import base64
from io import BytesIO

# =============================================================================
# IMPORT DU GESTIONNAIRE DE DONNÉES
# =============================================================================
from data_manager import load_data

# Charger les données dynamiques depuis le fichier JSON
data = load_data()

STATS = data["STATS"]
TODAY_STATS = data["TODAY_STATS"]
ACTUALITES = data["ACTUALITES"]
PROJETS_UNE = data["PROJETS_UNE"]
REPARTITION = data["REPARTITION"]
DEPARTEMENTS = data["DEPARTEMENTS"]
EVENEMENTS = data["EVENEMENTS"]
ACCORDS = data["ACCORDS"]
DOCUMENTS = data["DOCUMENTS"]
MOTS_CLES = data["MOTS_CLES"]

# =============================================================================
# CONFIGURATION PAGE
# =============================================================================
st.set_page_config(
    page_title="DGFD - Plateforme Nationale du Financement du Développement",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CSS CUSTOM COMPLET
# =============================================================================
CSS_CUSTOM = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main > div {
        padding-top: 0 !important;
    }
    
    .block-container {
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    
    /* ===== HEADER ===== */
    .dgfd-header {
        background-color: #ffffff;
        border-bottom: 1px solid #e5e7eb;
        padding: 0.5rem 4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    .dgfd-logo-text {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .dgfd-logo-badge {
        width: 48px;
        height: 48px;
        background-color: #0a2540;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #f2c94c;
        font-size: 20px;
        font-weight: bold;
    }
    
    .dgfd-logo-title {
        font-size: 13px;
        font-weight: 700;
        color: #0a2540;
        line-height: 1.2;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .dgfd-logo-subtitle {
        font-size: 9px;
        color: #6b7280;
        font-weight: 500;
    }
    
    .dgfd-nav {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .dgfd-nav a {
        text-decoration: none;
        color: #374151;
        font-size: 14px;
        font-weight: 500;
        transition: color 0.2s;
    }
    
    .dgfd-nav a:hover, .dgfd-nav a.active {
        color: #0a2540;
        font-weight: 600;
    }
    
    .dgfd-btn-login {
        background-color: #0a2540;
        color: white !important;
        padding: 8px 20px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        text-decoration: none;
    }
    
    /* ===== HERO SECTION ===== */
    .hero-section {
        position: relative;
        min-height: 420px;
        background: url('https://images.unsplash.com/photo-1509391366360-2e959784a276?w=1400&h=600&fit=crop') center/cover no-repeat;
        display: flex;
        align-items: center;
        padding: 0 4rem;
    }
    
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(10, 37, 64, 0.15);
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .hero-left {
        max-width: 500px;
    }
    
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: #0a2540;
        line-height: 1.15;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 15px;
        color: #374151;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    
    .hero-buttons {
        display: flex;
        gap: 12px;
    }
    
    .btn-green {
        background-color: #28a745;
        color: white !important;
        padding: 12px 24px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 14px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: none;
        cursor: pointer;
    }
    
    .btn-white {
        background-color: white;
        color: #0a2540 !important;
        padding: 12px 24px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 14px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid #d1d5db;
        cursor: pointer;
    }
    
    .today-box {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        min-width: 260px;
    }
    
    .today-title {
        font-size: 16px;
        font-weight: 700;
        color: #0a2540;
        margin-bottom: 16px;
    }
    
    .today-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 14px;
    }
    
    .today-icon {
        width: 36px;
        height: 36px;
        background: #f3f4f6;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }
    
    .today-value {
        font-size: 22px;
        font-weight: 800;
        color: #0a2540;
        line-height: 1;
    }
    
    .today-label {
        font-size: 11px;
        color: #6b7280;
        font-weight: 500;
    }
    
    .today-link {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #0a2540;
        font-size: 12px;
        font-weight: 600;
        text-decoration: none;
        margin-top: 8px;
    }
    
    /* ===== STATS ROW ===== */
    .stats-section {
        background: white;
        padding: 2rem 4rem;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 1.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .stat-card {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 16px;
        border-radius: 12px;
        transition: transform 0.2s;
    }
    
    .stat-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }
    
    .stat-icon.blue { background: #eff6ff; }
    .stat-icon.green { background: #f0fdf4; }
    .stat-icon.purple { background: #faf5ff; }
    .stat-icon.yellow { background: #fefce8; }
    .stat-icon.teal { background: #f0fdfa; }
    .stat-icon.gray { background: #f9fafb; }
    
    .stat-value {
        font-size: 24px;
        font-weight: 800;
        color: #0a2540;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 12px;
        color: #6b7280;
        font-weight: 500;
        margin-top: 4px;
        line-height: 1.3;
    }
    
    .stat-sublabel {
        font-size: 11px;
        color: #9ca3af;
        margin-top: 2px;
    }
    
    /* ===== SECTIONS ===== */
    .section-wrapper {
        padding: 2.5rem 4rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #0a2540;
    }
    
    .section-link {
        color: #0a2540;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* ===== NEWS CARDS ===== */
    .news-item {
        display: flex;
        gap: 16px;
        padding: 16px 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .news-item:last-child {
        border-bottom: none;
    }
    
    .news-thumb {
        width: 100px;
        height: 70px;
        border-radius: 8px;
        object-fit: cover;
        flex-shrink: 0;
    }
    
    .news-title {
        font-size: 14px;
        font-weight: 600;
        color: #0a2540;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    
    .news-date {
        font-size: 11px;
        color: #9ca3af;
        font-weight: 500;
        margin-bottom: 4px;
    }
    
    .news-excerpt {
        font-size: 12px;
        color: #6b7280;
        line-height: 1.4;
        margin-bottom: 6px;
    }
    
    .news-readmore {
        font-size: 12px;
        color: #0a2540;
        font-weight: 600;
        text-decoration: none;
    }
    
    /* ===== PROJECT CARDS ===== */
    .project-card {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
        background: white;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .project-image {
        width: 100%;
        height: 140px;
        object-fit: cover;
    }
    
    .project-tag {
        position: absolute;
        bottom: 8px;
        left: 8px;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 9px;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .project-body {
        padding: 16px;
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    .project-title {
        font-size: 16px;
        font-weight: 700;
        color: #0a2540;
        margin-bottom: 6px;
    }
    
    .project-partner {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 4px;
    }
    
    .project-amount {
        font-size: 18px;
        font-weight: 800;
        color: #0a2540;
        margin-bottom: 12px;
    }
    
    .project-link {
        margin-top: auto;
        font-size: 12px;
        color: #0a2540;
        font-weight: 600;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* ===== MAP SECTION ===== */
    .map-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e5e7eb;
        height: 100%;
    }
    
    .map-title {
        font-size: 16px;
        font-weight: 700;
        color: #0a2540;
        margin-bottom: 8px;
    }
    
    .map-hint {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 12px;
    }
    
    .map-select select {
        width: 100%;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #d1d5db;
        font-size: 13px;
        margin-bottom: 12px;
    }
    
    .map-stats {
        display: flex;
        gap: 20px;
        margin-bottom: 12px;
    }
    
    .map-stat-value {
        font-size: 20px;
        font-weight: 800;
        color: #0a2540;
    }
    
    .map-stat-label {
        font-size: 11px;
        color: #6b7280;
    }
    
    .map-partners-title {
        font-size: 12px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
    }
    
    .partner-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .partner-item {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 4px;
    }
    
    /* ===== CALENDAR ===== */
    .event-item {
        display: flex;
        gap: 14px;
        padding: 12px 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .event-date-box {
        width: 44px;
        height: 44px;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    
    .event-day {
        font-size: 16px;
        font-weight: 800;
        color: #0a2540;
        line-height: 1;
    }
    
    .event-month {
        font-size: 8px;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .event-title {
        font-size: 13px;
        font-weight: 600;
        color: #0a2540;
        margin-bottom: 2px;
    }
    
    .event-location {
        font-size: 11px;
        color: #9ca3af;
    }
    
    /* ===== TABLE ===== */
    .dgfd-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .dgfd-table th {
        text-align: left;
        padding: 10px 8px;
        font-size: 11px;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 2px solid #f3f4f6;
    }
    
    .dgfd-table td {
        padding: 10px 8px;
        font-size: 12px;
        color: #374151;
        border-bottom: 1px solid #f9fafb;
    }
    
    .dgfd-table tr:hover td {
        background: #f9fafb;
    }
    
    /* ===== DOCS ===== */
    .doc-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .doc-icon {
        width: 32px;
        height: 32px;
        background: #fef2f2;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #dc2626;
        font-size: 14px;
        flex-shrink: 0;
    }
    
    .doc-title {
        font-size: 12px;
        font-weight: 600;
        color: #374151;
        line-height: 1.3;
    }
    
    .doc-meta {
        font-size: 11px;
        color: #9ca3af;
    }
    
    /* ===== SEARCH & TAGS ===== */
    .search-box {
        width: 100%;
        padding: 10px 14px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        font-size: 13px;
        color: #6b7280;
        background: #f9fafb;
        margin-bottom: 16px;
    }
    
    .tags-title {
        font-size: 12px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 10px;
    }
    
    .tag-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .tag-item {
        padding: 6px 14px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        font-size: 12px;
        color: #374151;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .tag-item:hover {
        background: #0a2540;
        color: white;
        border-color: #0a2540;
    }
    
    /* ===== FOOTER ===== */
    .dgfd-footer {
        background: #0a2540;
        color: white;
        padding: 3rem 4rem 1.5rem;
        margin-top: 3rem;
    }
    
    .footer-grid {
        display: grid;
        grid-template-columns: 1.5fr 1fr 1fr 1fr;
        gap: 3rem;
        max-width: 1400px;
        margin: 0 auto 2rem;
    }
    
    .footer-brand {
        display: flex;
        gap: 12px;
        margin-bottom: 12px;
    }
    
    .footer-desc {
        font-size: 12px;
        color: #9ca3af;
        line-height: 1.6;
    }
    
    .footer-title {
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 16px;
        color: white;
    }
    
    .footer-links {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px 24px;
    }
    
    .footer-links a {
        color: #9ca3af;
        text-decoration: none;
        font-size: 12px;
        transition: color 0.2s;
    }
    
    .footer-links a:hover {
        color: white;
    }
    
    .footer-contact-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #9ca3af;
        font-size: 12px;
        margin-bottom: 8px;
    }
    
    .footer-social {
        display: flex;
        gap: 12px;
        margin-top: 12px;
    }
    
    .footer-social-icon {
        width: 32px;
        height: 32px;
        background: rgba(255,255,255,0.1);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
        text-decoration: none;
    }
    
    .footer-bottom {
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
        font-size: 11px;
        color: #6b7280;
    }
    
    .footer-bottom a {
        color: #9ca3af;
        text-decoration: none;
        margin-left: 20px;
    }
    
    /* ===== PIE CHART CENTER ===== */
    .pie-center-text {
        font-size: 28px;
        font-weight: 800;
        fill: #0a2540;
    }
    
    .pie-center-label {
        font-size: 12px;
        fill: #6b7280;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 1024px) {
        .stats-grid { grid-template-columns: repeat(3, 1fr); }
        .footer-grid { grid-template-columns: 1fr 1fr; }
        .hero-content { flex-direction: column; gap: 2rem; }
        .dgfd-nav { display: none; }
    }
    
    @media (max-width: 768px) {
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
        .footer-grid { grid-template-columns: 1fr; }
        .section-wrapper { padding: 1.5rem; }
        .hero-section { padding: 2rem; }
    }
</style>
"""

st.markdown(CSS_CUSTOM, unsafe_allow_html=True)

# =============================================================================
# FONCTIONS DE RENDU
# =============================================================================

def render_header():
    """Rendu du header avec navigation"""
    nav_items = [
        ("Accueil", True),
        ("Projets", False),
        ("Accords", False),
        ("Partenaires", False),
        ("Cartographie", False),
        ("Rapports", False),
        ("Actualités", False),
    ]
    
    nav_html = ""
    for label, active in nav_items:
        cls = 'active' if active else ''
        nav_html += f'<a href="#" class="{cls}">{label}</a>'
    
    header_html = f"""
    <div class="dgfd-header">
        <div class="dgfd-logo-text">
            <div class="dgfd-logo-badge">🇧🇯</div>
            <div>
                <div class="dgfd-logo-title">DGFD</div>
                <div class="dgfd-logo-subtitle">Direction Générale du Financement du Développement</div>
                <div class="dgfd-logo-subtitle">RÉPUBLIQUE DU BÉNIN</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 2rem;">
            <div class="dgfd-nav">
                {nav_html}
                <span style="color: #d1d5db;">🔍</span>
            </div>
            <a href="./Admin" target="_self" class="dgfd-btn-login">🔒 Admin</a>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_hero():
    """Section hero avec fond image et box aujourd'hui"""
    today_items = ""
    for item in TODAY_STATS:
        today_items += f"""
        <div class="today-item">
            <div class="today-icon">{item['icone']}</div>
            <div>
                <div class="today-value">{item['valeur']}</div>
                <div class="today-label">{item['label']}</div>
            </div>
        </div>
        """
    
    hero_html = f"""
    <div class="hero-section">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <div class="hero-left">
                <h1 class="hero-title">Plateforme Nationale du Financement du Développement</h1>
                <p class="hero-subtitle">
                    Une plateforme unique pour le suivi des accords, projets, partenaires techniques et financiers 
                    et indicateurs de développement du Bénin.
                </p>
                <div class="hero-buttons">
                    <a href="#" class="btn-green">📋 Consulter les projets</a>
                    <a href="#" class="btn-white">📊 Tableau de bord</a>
                </div>
            </div>
            <div class="today-box">
                <div class="today-title">Aujourd'hui</div>
                {today_items}
                <a href="#" class="today-link">Voir le tableau de bord →</a>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def render_stats():
    """Barre de statistiques"""
    icon_classes = {
        "📄": "blue",
        "📁": "green", 
        "👥": "purple",
        "🪙": "yellow",
        "🏛️": "teal",
        "✅": "gray",
    }
    
    stats_html = '<div class="stats-section"><div class="stats-grid">'
    for key, stat in STATS.items():
        icone = stat["icone"]
        cls = icon_classes.get(icone, "blue")
        stats_html += f"""
        <div class="stat-card">
            <div class="stat-icon {cls}">{icone}</div>
            <div>
                <div class="stat-value">{stat['valeur']}</div>
                <div class="stat-label">{stat['label']}</div>
                <div class="stat-sublabel">{stat['sublabel']}</div>
            </div>
        </div>
        """
    stats_html += '</div></div>'
    st.markdown(stats_html, unsafe_allow_html=True)


def render_news_and_projects():
    """Section Actualités + Projets à la une"""
    # Actualités
    news_html = ""
    for news in ACTUALITES:
        news_html += f"""
        <div class="news-item">
            <img src="{news['image']}" class="news-thumb" alt="{news['titre']}">
            <div>
                <div class="news-title">{news['titre']}</div>
                <div class="news-date">{news['date']}</div>
                <div class="news-excerpt">{news['resume']}</div>
                <a href="#" class="news-readmore">Lire la suite →</a>
            </div>
        </div>
        """
    
    # Projets
    projects_html = ""
    for proj in PROJETS_UNE:
        projects_html += f"""
        <div class="project-card">
            <div style="position: relative;">
                <img src="{proj['image']}" class="project-image" alt="{proj['titre']}">
                <span class="project-tag" style="background: {proj['couleur']};">{proj['categorie']}</span>
            </div>
            <div class="project-body">
                <div class="project-title">{proj['titre']}</div>
                <div class="project-partner">{proj['partenaire']}</div>
                <div class="project-amount">{proj['montant']}</div>
                <a href="#" class="project-link">Voir le projet →</a>
            </div>
        </div>
        """
    
    section_html = f"""
    <div class="section-wrapper">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3rem;">
            <div>
                <div class="section-header">
                    <div class="section-title">Actualités</div>
                    <a href="#" class="section-link">Voir toutes →</a>
                </div>
                {news_html}
            </div>
            <div>
                <div class="section-header">
                    <div class="section-title">Projets à la une</div>
                    <a href="#" class="section-link">Voir tous →</a>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                    {projects_html}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(section_html, unsafe_allow_html=True)


def render_pie_chart():
    """Graphique en camembert répartition des projets"""
    fig = go.Figure(data=[go.Pie(
        labels=REPARTITION["Secteurs"],
        values=REPARTITION["Pourcentages"],
        hole=0.65,
        marker_colors=REPARTITION["Couleurs"],
        textinfo='none',
        hoverinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'
    )])
    
    fig.add_annotation(
        text=f"<b>{REPARTITION['Total']}</b><br><span style='font-size:11px'>Projets</span>",
        x=0.5, y=0.5,
        font_size=14,
        showarrow=False,
        font_color="#0a2540"
    )
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def render_map_section():
    """Carte interactive + Pie chart + Calendrier"""
    # Créer le sélecteur de département
    deps = list(DEPARTEMENTS.keys())
    
    col1, col2, col3 = st.columns([1.1, 1, 0.9])
    
    with col1:
        st.markdown('<div class="section-title" style="margin-bottom: 8px;">Carte interactive</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 12px; color: #6b7280; margin-bottom: 10px;">Cliquez sur un département pour voir les projets</div>', unsafe_allow_html=True)
        
        selected_dep = st.selectbox("Département", deps, label_visibility="collapsed")
        dep_data = DEPARTEMENTS[selected_dep]
        
        # Stats du département
        st.markdown(f"""
        <div style="display: flex; gap: 24px; margin: 12px 0;">
            <div>
                <div style="font-size: 22px; font-weight: 800; color: #0a2540;">{dep_data['projets']}</div>
                <div style="font-size: 11px; color: #6b7280;">Projets</div>
            </div>
            <div>
                <div style="font-size: 22px; font-weight: 800; color: #0a2540;">{dep_data['montant']}</div>
                <div style="font-size: 11px; color: #6b7280;">Milliards FCFA</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 8px;">Principaux partenaires</div>', unsafe_allow_html=True)
        colors = ["#28a745", "#1e5aa8", "#dc3545"]
        for i, partner in enumerate(dep_data['partenaires']):
            color = colors[i % len(colors)]
            st.markdown(f'<div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;"><span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: {color}; margin-right: 6px;"></span>{partner}</div>', unsafe_allow_html=True)
        
        st.markdown('<br><a href="#" style="padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 12px; color: #374151; text-decoration: none; display: inline-block;">Voir tous les projets</a>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-title" style="margin-bottom: 4px;">Répartition des projets</div>', unsafe_allow_html=True)
        
        # Boutons toggle
        c1, c2 = st.columns(2)
        with c1:
            st.button("Par secteur", type="primary", use_container_width=True)
        with c2:
            st.button("Par partenaire", type="secondary", use_container_width=True)
        
        fig = render_pie_chart()
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Légende custom
        legend_html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px 12px; margin-top: 4px;">'
        for secteur, pct, couleur in zip(REPARTITION["Secteurs"], REPARTITION["Pourcentages"], REPARTITION["Couleurs"]):
            legend_html += f'''
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: {couleur};"></span>
                <span style="font-size: 11px; color: #6b7280;">{secteur}</span>
                <span style="font-size: 11px; color: #0a2540; font-weight: 600; margin-left: auto;">{pct}%</span>
            </div>
            '''
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="section-header" style="margin-bottom: 12px;"><div class="section-title">Calendrier des événements</div><a href="#" class="section-link">Voir tout →</a></div>', unsafe_allow_html=True)
        
        events_html = ""
        for evt in EVENEMENTS:
            events_html += f"""
            <div class="event-item">
                <div class="event-date-box">
                    <div class="event-day">{evt['jour']}</div>
                    <div class="event-month">{evt['mois']}</div>
                </div>
                <div>
                    <div class="event-title">{evt['titre']}</div>
                    <div class="event-location">{evt['lieu']}</div>
                </div>
            </div>
            """
        st.markdown(events_html, unsafe_allow_html=True)


def render_bottom_section():
    """Derniers accords + Documents + Recherche"""
    col1, col2, col3 = st.columns([1.2, 0.9, 0.9])
    
    with col1:
        st.markdown('<div class="section-header" style="margin-bottom: 8px;"><div class="section-title">Derniers accords signés</div><a href="#" class="section-link">Voir tous →</a></div>', unsafe_allow_html=True)
        
        table_rows = ""
        for acc in ACCORDS:
            table_rows += f"""
            <tr>
                <td style="font-weight: 600; color: #0a2540;">{acc['code']}</td>
                <td>{acc['projet']}</td>
                <td>{acc['partenaire']}</td>
                <td style="white-space: nowrap;">{acc['date']}</td>
            </tr>
            """
        
        st.markdown(f"""
        <table class="dgfd-table">
            <thead>
                <tr>
                    <th>Code Accord</th>
                    <th>Projet</th>
                    <th>Partenaire</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header" style="margin-bottom: 8px;"><div class="section-title">Documents récents</div><a href="#" class="section-link">Voir tous →</a></div>', unsafe_allow_html=True)
        
        docs_html = ""
        for doc in DOCUMENTS:
            docs_html += f"""
            <div class="doc-item">
                <div class="doc-icon">📄</div>
                <div>
                    <div class="doc-title">{doc['titre']}</div>
                    <div class="doc-meta">{doc['type']} · {doc['taille']}</div>
                </div>
            </div>
            """
        st.markdown(docs_html, unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="section-title" style="margin-bottom: 12px;">Recherche rapide</div>', unsafe_allow_html=True)
        st.markdown('<input type="text" class="search-box" placeholder="Rechercher un projet, accord, partenaire...">', unsafe_allow_html=True)
        st.markdown('<div class="tags-title">Mots-clés populaires</div>', unsafe_allow_html=True)
        
        tags_html = '<div class="tag-list">'
        for tag in MOTS_CLES:
            tags_html += f'<span class="tag-item">{tag}</span>'
        tags_html += '</div>'
        st.markdown(tags_html, unsafe_allow_html=True)


def render_footer():
    """Footer complet"""
    footer_html = """
    <div class="dgfd-footer">
        <div class="footer-grid">
            <div>
                <div class="footer-brand">
                    <div style="width: 48px; height: 48px; background: rgba(255,255,255,0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px;">🇧🇯</div>
                    <div>
                        <div style="font-size: 14px; font-weight: 700; color: white;">DGFD</div>
                        <div style="font-size: 10px; color: #9ca3af;">Direction Générale du Financement du Développement</div>
                    </div>
                </div>
                <div class="footer-desc">
                    Plateforme officielle de suivi des accords et projets de développement au Bénin.
                </div>
            </div>
            <div>
                <div class="footer-title">Liens rapides</div>
                <div class="footer-links">
                    <a href="#">Accueil</a>
                    <a href="#">Cartographie</a>
                    <a href="#">Projets</a>
                    <a href="#">Rapports</a>
                    <a href="#">Accords</a>
                    <a href="#">Actualités</a>
                    <a href="#">Partenaires</a>
                    <a href="#">Contact</a>
                </div>
            </div>
            <div>
                <div class="footer-title">Nous contacter</div>
                <div class="footer-contact-item">📍 Palais de la Marina<br>01 BP 302 Cotonou – Bénin</div>
                <div class="footer-contact-item">📞 +229 21 30 10 20</div>
                <div class="footer-contact-item">✉️ contact@dgfd.gov.bj</div>
            </div>
            <div>
                <div class="footer-title">Suivez-nous</div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <div style="width: 40px; height: 40px; background: rgba(255,255,255,0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center;">🇧🇯</div>
                    <div>
                        <div style="font-size: 10px; font-weight: 700; color: white;">RÉPUBLIQUE DU BÉNIN</div>
                        <div style="font-size: 9px; color: #9ca3af;">Fraternité - Justice - Travail</div>
                    </div>
                </div>
                <div class="footer-social">
                    <a href="#" class="footer-social-icon">f</a>
                    <a href="#" class="footer-social-icon">in</a>
                    <a href="#" class="footer-social-icon">▶</a>
                </div>
            </div>
        </div>
        <div class="footer-bottom">
            <div>© 2025 DGFD – Tous droits réservés</div>
            <div>
                <a href="#">Mentions légales</a>
                <a href="#">Confidentialité</a>
                <a href="#">Plan du site</a>
            </div>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

def main():
    render_header()
    render_hero()
    render_stats()
    render_news_and_projects()
    
    # Section carte + pie + calendrier
    st.markdown('<div class="section-wrapper" style="padding-top: 1rem;">', unsafe_allow_html=True)
    render_map_section()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section bottom
    st.markdown('<div class="section-wrapper" style="padding-top: 1rem;">', unsafe_allow_html=True)
    render_bottom_section()
    st.markdown('</div>', unsafe_allow_html=True)
    
    render_footer()


if __name__ == "__main__":
    main()
