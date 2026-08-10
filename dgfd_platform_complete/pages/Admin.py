import streamlit as st
import pandas as pd
import hashlib
import json
from datetime import datetime
import sys
import os

# Ajouter le parent au path pour importer data_manager et backup_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_manager import load_data, save_data, reset_data
from backup_manager import (
    create_backup, restore_backup, get_backup_stats, get_backup_files, get_backup_info,
    export_data_json, import_data_json
)

# =============================================================================
# CONFIGURATION PAGE
# =============================================================================
st.set_page_config(
    page_title="🔒 Administration DGFD",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CSS ADMIN
# =============================================================================
ADMIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main > div { padding-top: 1rem !important; }
    
    .admin-header {
        background: #0a2540;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .admin-title { font-size: 20px; font-weight: 700; margin: 0; }
    .admin-subtitle { font-size: 12px; color: #94a3b8; margin-top: 2px; }
    
    .stat-card-admin {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
    }
    .stat-card-admin .value { font-size: 28px; font-weight: 800; color: #0a2540; }
    .stat-card-admin .label { font-size: 12px; color: #6b7280; margin-top: 4px; }
    
    .section-box {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .section-title { font-size: 16px; font-weight: 700; color: #0a2540; margin-bottom: 1rem; }
    
    .btn-save {
        background: #28a745 !important;
        color: white !important;
    }
    .btn-danger {
        background: #dc3545 !important;
        color: white !important;
    }
    .btn-warning {
        background: #f2c94c !important;
        color: #0a2540 !important;
    }
    
    .success-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 12px 16px;
        color: #166534;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 12px 16px;
        color: #1e40af;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    .warning-box {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 8px;
        padding: 12px 16px;
        color: #92400e;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    .preview-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .preview-card .title { font-size: 13px; font-weight: 600; color: #0a2540; }
    .preview-card .meta { font-size: 11px; color: #6b7280; }
    
    .backup-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .backup-card .name { font-size: 13px; font-weight: 600; color: #0a2540; }
    .backup-card .meta { font-size: 11px; color: #6b7280; }
</style>
"""
st.markdown(ADMIN_CSS, unsafe_allow_html=True)

# =============================================================================
# AUTHENTIFICATION
# =============================================================================

ADMIN_HASH = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # "password"

def check_password(password):
    return hashlib.sha256(password.encode()).hexdigest() == ADMIN_HASH


def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="width: 64px; height: 64px; background: #0a2540; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 28px; color: #f2c94c; margin-bottom: 16px;">🇧🇯</div>
            <h2 style="color: #0a2540; margin-bottom: 4px;">Administration DGFD</h2>
            <p style="color: #6b7280; font-size: 14px;">Accès réservé aux administrateurs</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Identifiant", placeholder="admin")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••")
            submitted = st.form_submit_button("Se connecter", use_container_width=True, type="primary")
            
            if submitted:
                if username == "admin" and check_password(password):
                    st.session_state.authenticated = True
                    st.session_state.admin_user = username
                    st.rerun()
                else:
                    st.error("Identifiants incorrects. Veuillez réessayer.")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem; font-size: 12px; color: #9ca3af;">
            Identifiant par défaut : <b>admin</b> / Mot de passe : <b>password</b>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INIT
# =============================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "admin_menu" not in st.session_state:
    st.session_state.admin_menu = "Dashboard"
if "save_success" not in st.session_state:
    st.session_state.save_success = False

# =============================================================================
# REDIRECTION SI NON AUTHENTIFIÉ
# =============================================================================
if not st.session_state.authenticated:
    login_page()
    st.stop()

# =============================================================================
# SIDEBAR ADMIN
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <div style="width: 48px; height: 48px; background: #0a2540; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 20px; color: #f2c94c;">🇧🇯</div>
        <div style="font-size: 13px; font-weight: 700; color: #0a2540; margin-top: 6px;">DGFD Admin</div>
        <div style="font-size: 10px; color: #9ca3af;">Connecté : <b>{}</b></div>
    </div>
    """.format(st.session_state.get("admin_user", "admin")), unsafe_allow_html=True)
    
    menu = st.radio("Menu", [
        "📊 Dashboard",
        "📈 Stats",
        "📅 Aujourd'hui",
        "📰 Actualités",
        "🚀 Projets",
        "🥧 Répartition",
        "🗺️ Départements",
        "📆 Événements",
        "📋 Accords",
        "📄 Documents",
        "🏷️ Mots-clés",
        "💾 Sauvegardes",
        "🔄 Réinitialiser",
    ], label_visibility="collapsed")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🔓 Déconnexion", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.admin_menu = "Dashboard"
        st.rerun()
    
    st.markdown("""
    <div style="font-size: 10px; color: #9ca3af; text-align: center; margin-top: 1rem;">
        DGFD Admin v1.1<br>Plateforme Nationale du Financement du Développement
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================
data = load_data()

# =============================================================================
# AFFICHAGE DES NOTIFICATIONS
# =============================================================================
if st.session_state.save_success:
    st.markdown('<div class="success-box">✅ Modifications sauvegardées avec succès !</div>', unsafe_allow_html=True)
    st.session_state.save_success = False

# =============================================================================
# SECTION : DASHBOARD
# =============================================================================
if menu == "📊 Dashboard":
    st.markdown("""
    <div class="admin-header">
        <div>
            <div class="admin-title">📊 Tableau de bord</div>
            <div class="admin-subtitle">Vue d'ensemble des données de la plateforme</div>
        </div>
        <div style="font-size: 12px; color: #94a3b8;">
            Dernière mise à jour : {} {}
        </div>
    </div>
    """.format(datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M")), unsafe_allow_html=True)
    
    cols = st.columns(4)
    metrics = [
        (len(data["ACTUALITES"]), "Actualités", "📰"),
        (len(data["PROJETS_UNE"]), "Projets à la une", "🚀"),
        (len(data["EVENEMENTS"]), "Événements", "📆"),
        (len(data["ACCORDS"]), "Accords signés", "📋"),
    ]
    for col, (val, label, icon) in zip(cols, metrics):
        col.markdown(f"""
        <div class="stat-card-admin">
            <div style="font-size: 24px; margin-bottom: 4px;">{icon}</div>
            <div class="value">{val}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    cols2 = st.columns(4)
    metrics2 = [
        (len(data["DOCUMENTS"]), "Documents", "📄"),
        (len(data["DEPARTEMENTS"]), "Départements", "🗺️"),
        (data["REPARTITION"]["Total"], "Total Projets", "📈"),
        (len(data["MOTS_CLES"]), "Mots-clés", "🏷️"),
    ]
    for col, (val, label, icon) in zip(cols2, metrics2):
        col.markdown(f"""
        <div class="stat-card-admin">
            <div style="font-size: 24px; margin-bottom: 4px;">{icon}</div>
            <div class="value">{val}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📰 Aperçu des actualités</div>', unsafe_allow_html=True)
        for news in data["ACTUALITES"][:3]:
            st.markdown(f"""
            <div class="preview-card">
                <div class="title">{news['titre']}</div>
                <div class="meta">{news['date']} · {news['categorie']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🚀 Aperçu des projets</div>', unsafe_allow_html=True)
        for proj in data["PROJETS_UNE"]:
            st.markdown(f"""
            <div class="preview-card">
                <div class="title">{proj['titre']}</div>
                <div class="meta">{proj['partenaire']} · {proj['montant']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Répartition des projets par secteur</div>', unsafe_allow_html=True)
    rep_data = pd.DataFrame({
        "Secteur": data["REPARTITION"]["Secteurs"],
        "%": data["REPARTITION"]["Pourcentages"],
        "Couleur": data["REPARTITION"]["Couleurs"]
    })
    st.dataframe(rep_data, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SECTION : STATS
# =============================================================================
elif menu == "📈 Stats":
    st.markdown('<div class="admin-header"><div><div class="admin-title">📈 Chiffres clés</div><div class="admin-subtitle">Modifier les 6 indicateurs de la barre de statistiques</div></div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">ℹ️ Ces valeurs apparaissent dans la barre de statistiques sous le hero section.</div>', unsafe_allow_html=True)
    
    with st.form("stats_form"):
        cols = st.columns(2)
        stats_keys = list(data["STATS"].keys())
        new_stats = {}
        
        for i, key in enumerate(stats_keys):
            with cols[i % 2]:
                st.markdown(f"**{key.replace('_', ' ').title()}**")
                stat = data["STATS"][key]
                icon = st.text_input(f"Icône {i+1}", value=stat["icone"], key=f"stat_icon_{key}")
                val = st.text_input(f"Valeur {i+1}", value=str(stat["valeur"]), key=f"stat_val_{key}")
                label = st.text_input(f"Label {i+1}", value=stat["label"], key=f"stat_label_{key}")
                sublabel = st.text_input(f"Sous-label {i+1}", value=stat["sublabel"], key=f"stat_sub_{key}")
                new_stats[key] = {"icone": icon, "valeur": val, "label": label, "sublabel": sublabel}
                st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submitted = st.form_submit_button("💾 Sauvegarder", use_container_width=True, type="primary")
        
        if submitted:
            data["STATS"] = new_stats
            save_data(data)
            st.session_state.save_success = True
            st.rerun()


# =============================================================================
# SECTION : AUJOURD'HUI
# =============================================================================
elif menu == "📅 Aujourd'hui":
    st.markdown('<div class="admin-header"><div><div class="admin-title">📅 Box "Aujourd\'hui"</div><div class="admin-subtitle">Modifier les 3 indicateurs de la boîte en haut à droite</div></div></div>', unsafe_allow_html=True)
    
    df_today = pd.DataFrame(data["TODAY_STATS"])
    st.markdown('<div class="info-box">✏️ Vous pouvez modifier directement dans le tableau ci-dessous. Cliquez sur une cellule pour l\'éditer.</div>', unsafe_allow_html=True)
    
    edited = st.data_editor(
        df_today,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "icone": st.column_config.TextColumn("Icône"),
            "valeur": st.column_config.TextColumn("Valeur"),
            "label": st.column_config.TextColumn("Label"),
        },
        hide_index=True,
        key="editor_today"
    )
    
    if st.button("💾 Sauvegarder les modifications", type="primary"):
        data["TODAY_STATS"] = edited.to_dict("records")
        save_data(data)
        st.session_state.save_success = True
        st.rerun()


# =============================================================================
# SECTION : ACTUALITÉS
# =============================================================================
elif menu == "📰 Actualités":
    st.markdown('<div class="admin-header"><div><div class="admin-title">📰 Actualités</div><div class="admin-subtitle">Gérer les articles d\'actualité (ajouter, modifier, supprimer)</div></div></div>', unsafe_allow_html=True)
    
    df_news = pd.DataFrame(data["ACTUALITES"])
    st.markdown('<div class="info-box">✏️ Utilisez le tableau ci-dessous pour modifier les actualités. Ajoutez des lignes avec le bouton + en bas, ou supprimez avec la corbeille.</div>', unsafe_allow_html=True)
    
    edited = st.data_editor(
        df_news,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "titre": st.column_config.TextColumn("Titre", width="large"),
            "date": st.column_config.TextColumn("Date"),
            "resume": st.column_config.TextColumn("Résumé", width="large"),
            "image": st.column_config.TextColumn("URL Image"),
            "categorie": st.column_config.TextColumn("Catégorie"),
        },
        hide_index=True,
        key="editor_news"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("💾 Sauvegarder", type="primary", use_container_width=True):
            data["ACTUALITES"] = edited.to_dict("records")
            save_data(data)
            st.session_state.save_success = True
            st.rerun()
    
    # Aperçu
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">👁️ Aperçu des actualités</div>', unsafe_allow_html=True)
    for news in edited.to_dict("records"):
        with st.container():
            cols = st.columns([1, 4])
            with cols[0]:
                st.image(news.get("image", ""), width=100)
            with cols[1]:
                st.markdown(f"**{news['titre']}**  
<small>{news['date']} · {news['categorie']}</small>  
{news['resume']}</small>", unsafe_allow_html=True)
            st.markdown("---")


# =============================================================================
# SECTION : PROJETS
# =============================================================================
elif menu == "🚀 Projets":
    st.markdown('<div class="admin-header"><div><div class="admin-title">🚀 Projets à la une</div><div class="admin-subtitle">Gérer les 3 projets mis en avant sur la page d\'accueil</div></div></div>', unsafe_allow_html=True)
    
    df_proj = pd.DataFrame(data["PROJETS_UNE"])
    st.markdown('<div class="info-box">✏️ Modifiez les projets dans le tableau. Le champ "couleur" doit être un code hexadécimal (ex: #28a745).</div>', unsafe_allow_html=True)
    
    edited = st.data_editor(
        df_proj,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "titre": st.column_config.TextColumn("Titre"),
            "partenaire": st.column_config.TextColumn("Partenaire"),
            "montant": st.column_config.TextColumn("Montant"),
            "image": st.column_config.TextColumn("URL Image"),
            "categorie": st.column_config.TextColumn("Catégorie"),
            "couleur": st.column_config.TextColumn("Couleur (hex)"),
        },
        hide_index=True,
        key="editor_projets"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("💾 Sauvegarder", type="primary", use_container_width=True):
            data["PROJETS_UNE"] = edited.to_dict("records")
            save_data(data)
            st.session_state.save_success = True
            st.rerun()
    
    # Aperçu couleurs
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎨 Aperçu des couleurs</div>', unsafe_allow_html=True)
    cols = st.columns(len(edited))
    for i, (_, proj) in enumerate(edited.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div style="background: {proj['couleur']}; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: 600; font-size: 13px;">
                {proj['categorie']}
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# SECTION : RÉPARTITION
# =============================================================================
elif menu == "🥧 Répartition":
    st.markdown('<div class="admin-header"><div><div class="admin-title">🥧 Répartition des projets</div><div class="admin-subtitle">Modifier les secteurs et pourcentages du graphique camembert</div></div></div>', unsafe_allow_html=True)
    
    rep = data["REPARTITION"]
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Données</div>', unsafe_allow_html=True)
        
        df_rep = pd.DataFrame({
            "Secteur": rep["Secteurs"],
            "Pourcentage": rep["Pourcentages"],
            "Couleur": rep["Couleurs"]
        })
        
        edited = st.data_editor(
            df_rep,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Secteur": st.column_config.TextColumn("Secteur"),
                "Pourcentage": st.column_config.NumberColumn("%", min_value=0, max_value=100, step=1),
                "Couleur": st.column_config.TextColumn("Couleur hex"),
            },
            hide_index=True,
            key="editor_repartition"
        )
        
        total = st.number_input("Total projets", value=rep["Total"], min_value=0, step=1)
        
        if st.button("💾 Sauvegarder", type="primary"):
            data["REPARTITION"] = {
                "Secteurs": edited["Secteur"].tolist(),
                "Pourcentages": edited["Pourcentage"].tolist(),
                "Couleurs": edited["Couleur"].tolist(),
                "Total": total
            }
            save_data(data)
            st.session_state.save_success = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        import plotly.graph_objects as go
        fig = go.Figure(data=[go.Pie(
            labels=edited["Secteur"].tolist(),
            values=edited["Pourcentage"].tolist(),
            hole=0.65,
            marker_colors=edited["Couleur"].tolist(),
            textinfo='none',
            hoverinfo='label+percent',
        )])
        fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:11px'>Projets</span>", x=0.5, y=0.5, font_size=14, showarrow=False, font_color="#0a2540")
        fig.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


# =============================================================================
# SECTION : DÉPARTEMENTS
# =============================================================================
elif menu == "🗺️ Départements":
    st.markdown('<div class="admin-header"><div><div class="admin-title">🗺️ Départements</div><div class="admin-subtitle">Gérer les données par département (projets, montants, partenaires)</div></div></div>', unsafe_allow_html=True)
    
    dep_flat = []
    for name, info in data["DEPARTEMENTS"].items():
        dep_flat.append({
            "nom": name,
            "projets": info["projets"],
            "montant": info["montant"],
            "partenaires": ", ".join(info["partenaires"])
        })
    
    df_dep = pd.DataFrame(dep_flat)
    st.markdown('<div class="info-box">✏️ Les partenaires doivent être séparés par des virgules. Ex: BAD, AFD, UE</div>', unsafe_allow_html=True)
    
    edited = st.data_editor(
        df_dep,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "nom": st.column_config.TextColumn("Département"),
            "projets": st.column_config.NumberColumn("Projets", min_value=0, step=1),
            "montant": st.column_config.NumberColumn("Montant (Mds FCFA)", min_value=0, step=1),
            "partenaires": st.column_config.TextColumn("Partenaires (séparés par virgules)"),
        },
        hide_index=True,
        key="editor_departements"
    )
    
    if st.button("💾 Sauvegarder", type="primary"):
        new_deps = {}
        for _, row in edited.iterrows():
            if pd.notna(row["nom"]) and str(row["nom"]).strip():
                new_deps[str(row["nom"]).strip()] = {
                    "projets": int(row["projets"]) if pd.notna(row["projets"]) else 0,
                    "montant": int(row["montant"]) if pd.notna(row["montant"]) else 0,
                    "partenaires": [p.strip() for p in str(row["partenaires"]).split(",") if p.strip()]
                }
        data["DEPARTEMENTS"] = new_deps
        save_data(data)
        st.session_state.save_success = True
        st.rerun()


# =============================================================================
# SECTION : ÉVÉNEMENTS
# =============================================================================
elif menu == "📆 Événements":
    st.markdown('<div class="admin-header"><div><div class="admin-title">📆 Calendrier des événements</div><div class="admin-subtitle">Gérer les événements affichés sur la page d\'accueil</div></div></div>', unsafe_allow_html=True)
    
    df_evt = pd.DataFrame(data["EVENEMENTS"])
    edited = st.data_editor(
        df_evt,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "jour": st.column_config.NumberColumn("Jour", min_value=1, max_value=31, step=1),
            "mois": st.column_config.TextColumn("Mois"),
            "titre": st.column_config.TextColumn("Titre"),
            "lieu": st.column_config.TextColumn("Lieu"),
        },
        hide_index=True,
        key="editor_evenements"
    )
    
    if st.button("💾 Sauvegarder", type="primary"):
        data["EVENEMENTS"] = edited.to_dict("records")
        save_data(data)
        st.session_state.save_success = True
        st.rerun()


# =============================================================================
# SECTION : ACCORDS
# =============================================================================
elif menu == "📋 Accords":
    st.markdown('<div class="admin-header"><div><div class="admin-title">📋 Accords signés</div><div class="admin-subtitle">Gérer les accords du tableau</div></div></div>', unsafe_allow_html=True)
    
    df_acc = pd.DataFrame(data["ACCORDS"])
    edited = st.data_editor(
        df_acc,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "code": st.column_config.TextColumn("Code"),
            "projet": st.column_config.TextColumn("Projet"),
            "partenaire": st.column_config.TextColumn("Partenaire"),
            "date": st.column_config.TextColumn("Date (JJ/MM/AAAA)"),
        },
        hide_index=True,
        key="editor_accords"
    )
    
    if st.button("💾 Sauvegarder", type="primary"):
        data["ACCORDS"] = edited.to_dict("records")
        save_data(data)
        st.session_state.save_success = True
        st.rerun()


# =============================================================================
# SECTION : DOCUMENTS
# =============================================================================
elif menu == "📄 Documents":
    st.markdown('<div class="admin-header"><div><div class="admin-title">📄 Documents récents</div><div class="admin-subtitle">Gérer la liste des documents téléchargeables</div></div></div>', unsafe_allow_html=True)
    
    df_doc = pd.DataFrame(data["DOCUMENTS"])
    edited = st.data_editor(
        df_doc,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "titre": st.column_config.TextColumn("Titre"),
            "type": st.column_config.TextColumn("Type"),
            "taille": st.column_config.TextColumn("Taille"),
        },
        hide_index=True,
        key="editor_documents"
    )
    
    if st.button("💾 Sauvegarder", type="primary"):
        data["DOCUMENTS"] = edited.to_dict("records")
        save_data(data)
        st.session_state.save_success = True
        st.rerun()


# =============================================================================
# SECTION : MOTS-CLÉS
# =============================================================================
elif menu == "🏷️ Mots-clés":
    st.markdown('<div class="admin-header"><div><div class="admin-title">🏷️ Mots-clés populaires</div><div class="admin-subtitle">Modifier les tags de recherche rapide</div></div></div>', unsafe_allow_html=True)
    
    mots_cles = data["MOTS_CLES"]
    mots_text = st.text_area(
        "Mots-clés (séparés par des virgules)",
        value=", ".join(mots_cles),
        height=120,
        help="Entrez les mots-clés séparés par des virgules. Ex: PROFAR, AQUA-VIE, Santé"
    )
    
    if st.button("💾 Sauvegarder", type="primary"):
        new_tags = [t.strip() for t in mots_text.split(",") if t.strip()]
        data["MOTS_CLES"] = new_tags
        save_data(data)
        st.session_state.save_success = True
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏷️ Aperçu des tags</div>', unsafe_allow_html=True)
    tags_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px;">'
    for tag in [t.strip() for t in mots_text.split(",") if t.strip()]:
        tags_html += f'<span style="padding: 6px 14px; background: white; border: 1px solid #e5e7eb; border-radius: 20px; font-size: 12px; color: #374151; font-weight: 500;">{tag}</span>'
    tags_html += '</div>'
    st.markdown(tags_html, unsafe_allow_html=True)


# =============================================================================
# SECTION : SAUVEGARDES
# =============================================================================
elif menu == "💾 Sauvegardes":
    st.markdown("""
    <div class="admin-header">
        <div>
            <div class="admin-title">💾 Gestion des sauvegardes</div>
            <div class="admin-subtitle">Sauvegarder, restaurer et exporter les données</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Statistiques ---
    stats = get_backup_stats()
    
    cols = st.columns(4)
    metrics = [
        (stats["count"], "Backups stockés", "💾"),
        (stats["total_size"], "Espace utilisé", "📦"),
        (stats["newest"]["date"] if stats["newest"] else "—", "Dernier backup", "🕐"),
        ("10", "Rotation (max)", "🔄"),
    ]
    for col, (val, label, icon) in zip(cols, metrics):
        col.markdown(f"""
        <div class="stat-card-admin">
            <div style="font-size: 24px; margin-bottom: 4px;">{icon}</div>
            <div class="value" style="font-size: 20px;">{val}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Actions rapides ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📦 Sauvegarde manuelle</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Crée une sauvegarde instantanée du fichier de données actuel.</div>', unsafe_allow_html=True)
        if st.button("💾 Créer un backup maintenant", type="primary", use_container_width=True):
            result = create_backup(label="manual")
            if result["success"]:
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📥 Export JSON</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Télécharger le fichier JSON actuel pour l\'archiver.</div>', unsafe_allow_html=True)
        json_content = export_data_json()
        if json_content:
            st.download_button(
                label="📥 Télécharger le JSON",
                data=json_content,
                file_name=f"dgfd_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📤 Import JSON</div>', unsafe_allow_html=True)
        st.markdown('<div class="warning-box">⚠️ Remplace toutes les données actuelles. Un backup auto sera créé.</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choisir un fichier JSON", type=["json"], label_visibility="collapsed")
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                if st.button("📤 Importer", type="primary", use_container_width=True):
                    result = import_data_json(content)
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
            except Exception as e:
                st.error(f"❌ Erreur de lecture : {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Liste des backups ---
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Backups disponibles</div>', unsafe_allow_html=True)
    
    backups = get_backup_files()
    
    if not backups:
        st.info("ℹ️ Aucun backup trouvé. Les backups sont créés automatiquement à chaque sauvegarde.")
    else:
        for i, backup in enumerate(backups):
            info = get_backup_info(backup)
            with st.container():
                cols = st.columns([4, 1, 1])
                with cols[0]:
                    st.markdown(f"""
                    <div class="backup-card">
                        <div>
                            <div class="name">{info['filename']}</div>
                            <div class="meta">{info['date']} · {info['size']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    if st.button("🔄 Restaurer", key=f"restore_{i}", use_container_width=True):
                        result = restore_backup(str(backup))
                        if result["success"]:
                            st.success(result["message"])
                            st.rerun()
                        else:
                            st.error(result["message"])
                with cols[2]:
                    # Créer le fichier pour téléchargement
                    with open(backup, 'rb') as f:
                        file_data = f.read()
                    st.download_button(
                        label="⬇️",
                        data=file_data,
                        file_name=info['filename'],
                        mime="application/gzip" if info['filename'].endswith('.gz') else "application/json",
                        key=f"download_{i}",
                        use_container_width=True
                    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Commandes CLI ---
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💻 Commandes en ligne (CLI)</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Utilisez ces commandes pour automatiser les backups via cron ou tâches planifiées.</div>', unsafe_allow_html=True)
    
    st.code("""# Créer une sauvegarde manuelle
python backup_manager.py --backup

# Lister les backups
python backup_manager.py --list

# Restaurer un backup (spécifier le chemin)
python backup_manager.py --restore backups/dgfd_backup_20260101_120000_auto.json.gz

# Nettoyer les vieux backups
python backup_manager.py --cleanup

# Afficher les statistiques
python backup_manager.py --stats

# Backup planifié (cron) - toutes les heures
# crontab -e
# 0 * * * * cd /chemin/vers/dgfd && python backup_manager.py --backup
""", language="bash")
    st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# SECTION : RÉINITIALISER
# =============================================================================
elif menu == "🔄 Réinitialiser":
    st.markdown('<div class="admin-header"><div><div class="admin-title">🔄 Réinitialiser les données</div><div class="admin-subtitle">Restaurer les données aux valeurs par défaut</div></div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.warning("⚠️ Attention : Cette action va supprimer toutes les modifications personnalisées et restaurer les données d'origine.")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Réinitialiser tout", type="primary", use_container_width=True):
            reset_data()
            st.success("✅ Données réinitialisées avec succès !")
            st.info("Rafraîchissez la page pour voir les données par défaut.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Données JSON actuelles</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Vous pouvez copier ce JSON pour faire une sauvegarde manuelle.</div>', unsafe_allow_html=True)
    st.json(data)
    st.markdown('</div>', unsafe_allow_html=True)
