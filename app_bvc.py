import datetime
import json
import math
import os
import random
import sqlite3
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

# Configuración general de la página
st.set_page_config(
    page_title="BCV By Jp - Terminal Financiera",
    page_icon="📈",
    layout="wide",
)

# ==========================================
# ESTILOS CSS DE VANGUARDIA (AVATAR ANIMADO JP)
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Roboto+Mono:wght@500;700&display=swap');

    .stApp {
        background-color: #060913;
        color: #f0f6fc;
        font-family: 'Inter', sans-serif;
    }
    
    .price-tag {
        font-family: 'Roboto Mono', monospace;
        font-weight: 700;
        color: #2ea043;
    }

    body {
        background: 
            linear-gradient(rgba(4, 8, 18, 0.88), rgba(4, 8, 18, 0.95)),
            url("fondo-financiero.jpg") center/cover no-repeat fixed;
    }
    .login-container {
        background: rgba(13, 20, 36, 0.82);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(88, 166, 255, 0.25);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
        border-radius: 24px;
        padding: 35px;
    }

    .asset-card {
        background: linear-gradient(135deg, #101622 0%, #1a2233 100%);
        border: 1px solid rgba(31, 111, 235, 0.4);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .asset-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
        box-shadow: 0 15px 35px rgba(88, 166, 255, 0.3);
    }

    /* Caja del Guía Virtual JP */
    .guide-box {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%);
        border: 2px solid #facc15;
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 0 25px rgba(250, 204, 21, 0.25);
    }

    /* Animación de flotación y brillo para la foto de JP */
    .jp-avatar {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #facc15;
        box-shadow: 0 0 20px rgba(250, 204, 21, 0.6);
        animation: floatJp 3.5s ease-in-out infinite;
    }

    @keyframes floatJp {
        0% { transform: translateY(0px) scale(1); box-shadow: 0 0 15px rgba(250, 204, 21, 0.5); }
        50% { transform: translateY(-8px) scale(1.03); box-shadow: 0 0 28px rgba(250, 204, 21, 0.8); }
        100% { transform: translateY(0px) scale(1); box-shadow: 0 0 15px rgba(250, 204, 21, 0.5); }
    }

    .hero-planet-box {
        background: radial-gradient(circle at center, #1b2a4a 0%, #0a0e1a 75%);
        border: 2px solid #58a6ff;
        border-radius: 28px;
        padding: 45px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 45px rgba(88, 166, 255, 0.25);
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #0f172a, #080d16);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.5);
    }

    h1, h2, h3 { color: #58a6ff; font-weight: 700; }

    .stButton>button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; border-radius: 12px; border: none; font-weight: 600; padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 14px rgba(35, 134, 54, 0.4); transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(46, 160, 67, 0.6); }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# BASE DE DATOS Y ESTADOS
# ==========================================
DB_FILE = "bcv_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password TEXT, rol TEXT, semestre TEXT, carrera TEXT,
            cash REAL, presupuesto_inicial REAL, portfolio_acciones TEXT, cdt_list TEXT,
            renta_fija_list TEXT, historial_pasos TEXT, informe_estudiante TEXT, esg_fund REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            titulo TEXT PRIMARY KEY, descripcion TEXT, tendencia_forzada TEXT,
            semestre_objetivo TEXT, presupuesto_inicial REAL, eventos_claves TEXT, entregas TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@st.cache_data
def load_user_db_cached():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    db = {}
    for row in rows:
        if len(row) == 12:
            uname, rol, sem, car, cash, p_ini, p_acc, c_list, r_list, h_pas, inf, esg = row
            pwd = "123"
        else:
            uname, pwd, rol, sem, car, cash, p_ini, p_acc, c_list, r_list, h_pas, inf, esg = row
        
        try: p_acc = json.loads(p_acc) if p_acc else {}
        except: p_acc = {}
        try: c_list = json.loads(c_list) if c_list else []
        except: c_list = []
        try: r_list = json.loads(r_list) if r_list else []
        except: r_list = []
        try: h_pas = json.loads(h_pas) if h_pas else []
        except: h_pas = []

        db[uname] = {
            "password": pwd, "rol": rol, "semestre": sem, "carrera": car,
            "cash": cash, "presupuesto_inicial": p_ini,
            "portfolio_acciones": p_acc, "cdt_list": c_list,
            "renta_fija_list": r_list, "historial_pasos": h_pas,
            "informe_estudiante": inf, "esg_fund": esg
        }
    conn.close()
    return db

def save_user_to_db(username, udata):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        username, udata.get("password", "123"), udata.get("rol"), udata.get("semestre"),
        udata.get("carrera"), udata.get("cash"), udata.get("presupuesto_inicial"),
        json.dumps(udata.get("portfolio_acciones")), json.dumps(udata.get("cdt_list")),
        json.dumps(udata.get("renta_fija_list")), json.dumps(udata.get("historial_pasos")),
        udata.get("informe_estudiante"), udata.get("esg_fund")
    ))
    conn.commit()
    conn.close()

if "user_database" not in st.session_state:
    st.session_state.user_database = load_user_db_cached()

if "current_date" not in st.session_state:
    st.session_state.current_date = datetime.date(2026, 10, 3)

# ==========================================
# GENERADOR DE PRECIOS
# ==========================================
if "stocks_initialized" not in st.session_state:
    base_data = {
        "ECOPETROL": {"precio": 2685, "logo": "🛢️", "desc": "Empresa Colombiana de Petróleos S.A."},
        "BCOLOMBIA": {"precio": 33500, "logo": "🏦", "desc": "Banco de Colombia S.A."},
        "ISA": {"precio": 18900, "logo": "⚡", "desc": "Interconexión Eléctrica S.A."},
        "GRUPOSURA": {"precio": 36200, "logo": "📈", "desc": "Grupo de Inversiones Suramericana."}
    }
    st.session_state.prices_dict = base_data
    st.session_state.prices = {k: v["precio"] for k, v in base_data.items()}
    st.session_state.stocks_initialized = True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# LOGIN
# ==========================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; min-height: 82vh;">
            <div class="login-container" style="width: 100%; max-width: 480px;">
                <h1 style="text-align: center; color: #58a6ff; font-size: 2.2rem; margin-bottom: 5px;">🔐 BCV By Jp</h1>
                <h3 style="text-align: center; color: #8b949e; font-size: 1rem; margin-bottom: 25px;">Portal Académico Financiero</h3>
        """, unsafe_allow_html=True
    )
    with st.form("form_est"):
        nombre_est = st.text_input("Nombre Completo:")
        pass_est = st.text_input("Contraseña:", type="password")
        btn_ing = st.form_submit_button("Ingresar al Portal 🚀")
        if btn_ing and nombre_est.strip() and pass_est.strip():
            if nombre_est not in st.session_state.user_database:
                st.session_state.user_database[nombre_est] = {
                    "password": pass_est, "rol": "Estudiante", "semestre": "Semestre 5",
                    "carrera": "Administración", "cash": 500000, "presupuesto_inicial": 500000,
                    "portfolio_acciones": {}, "cdt_list": [], "renta_fija_list": [],
                    "historial_pasos": [], "informe_estudiante": "", "esg_fund": 0
                }
                save_user_to_db(nombre_est, st.session_state.user_database[nombre_est])
            st.session_state.current_user = nombre_est
            st.session_state.current_role = "Estudiante"
            st.session_state.logged_in = True
            st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# NAVEGACIÓN
# ==========================================
usuario_activo = st.session_state.current_user
u_data = st.session_state.user_database[usuario_activo]

with st.sidebar:
    st.title("📈 BCV By Jp")
    st.success(f"👤 **{usuario_activo}**")
    
    menu = option_menu(
        "Navegación",
        ["Guía Virtual Jp", "Terminal Bursátil", "Catálogo Técnico"],
        icons=["person-badge", "cart", "graph-up"],
        menu_icon="cast", default_index=0
    )

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# GUÍA VIRTUAL "JP" ANIMADO
# ==========================================
def render_guia_jp():
    # Comprobar si existe la imagen guardada
    has_img = os.path.exists("jp_foto.jpg")

    col_a, col_b = st.columns([0.25, 0.75])
    with col_a:
        if has_img:
            import base64
            with open("jp_foto.jpg", "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{img_b64}" class="jp-avatar" /></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<div style="font-size: 4rem; text-align: center;">👨‍💼</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown(
            f"""
            <div class="guide-box">
                <h2 style="color: #facc15; margin: 0; font-size: 1.6rem;">🟡 Jp - Tu Guía Virtual Unisucre</h2>
                <p style="color: #e2e8f0; margin-top: 5px; font-size: 1rem;">
                    ¡Habla, <b>{usuario_activo}</b>! Soy <b>Jp</b>. Estoy listo para ayudarte a moverte en la bolsa, tomar las mejores decisiones financieras y romperla en la simulación.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    col_g1, col_g2 = st.columns([1, 1])

    with col_g1:
        st.markdown("### 🧭 ¿Qué paso quieres dar hoy?")
        opcion = st.selectbox(
            "Selecciona una recomendación de Jp:",
            [
                "1. ¿Cómo compro acciones en la Terminal?",
                "2. ¿Cómo diversifico mi capital?",
                "3. ¿Cómo reviso mi rentabilidad?"
            ]
        )
        if "1. ¿Cómo" in opcion:
            st.info("💡 **Jp te aconseja:** Ve a la **Terminal Bursátil**, elige la acción y dale en 'Comprar'. Recuerda tener efectivo libre.")
        elif "2. ¿Cómo" in opcion:
            st.info("💡 **Jp te aconseja:** No metas todos los huevos en la misma canasta. Combina acciones con CDT o Bonos de Renta Fija.")
        else:
            st.info("💡 **Jp te aconseja:** En la barra lateral siempre puedes ver tu **Patrimonio Total** actualizado en tiempo real.")

    with col_g2:
        st.markdown("### 💬 Pregúntale algo a Jp")
        preg = st.text_input("Escribe tu pregunta:")
        if preg:
            p_low = preg.lower()
            if "efectivo" in p_low or "saldo" in p_low:
                st.success(f"🟡 **Jp:** Tienes **${u_data['cash']:,.0f} COP** disponibles en caja para invertir.")
            elif "quien eres" in p_low or "nombre" in p_low:
                st.success("🟡 **Jp:** ¡Soy Juan Pablo López (Jp)! Creador y guía virtual de esta terminal bursátil en Unisucre.")
            else:
                st.success("🟡 **Jp:** ¡Anotado, cuadro! Cualquier duda puedes explorar los módulos de la barra lateral.")

if menu == "Guía Virtual Jp":
    render_guia_jp()
elif menu == "Terminal Bursátil":
    st.title("🛒 Terminal Bursátil")
    st.info("Módulo de compra y venta listo.")
elif menu == "Catálogo Técnico":
    st.title("📊 Catálogo Técnico")
    st.info("Módulo de análisis de precios.")