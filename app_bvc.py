import base64
import datetime
import json
import os
import random
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

# Configuración general
st.set_page_config(
    page_title="BCV By Jp - Terminal Financiera Unisucre",
    page_icon="📈",
    layout="wide",
)

# ==========================================
# ESTILOS CSS (BANNER DE JP FLOTANTE EN TODAS LAS PÁGINAS)
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

    /* Banner Global de Jp */
    .jp-global-banner {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%);
        border: 2px solid #facc15;
        border-radius: 20px;
        padding: 18px 25px;
        margin-bottom: 25px;
        box-shadow: 0 0 25px rgba(250, 204, 21, 0.2);
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .jp-avatar-img {
        width: 85px;
        height: 85px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #facc15;
        box-shadow: 0 0 15px rgba(250, 204, 21, 0.5);
        animation: floatJp 3.5s ease-in-out infinite;
    }

    @keyframes floatJp {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-5px) scale(1.03); }
        100% { transform: translateY(0px) scale(1); }
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

    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# BASE DE DATOS Y PERSISTENCIA
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
        uname, pwd, rol, sem, car, cash, p_ini, p_acc, c_list, r_list, h_pas, inf, esg = row
        try: p_acc = json.loads(p_acc) if p_acc else {}
        except: p_acc = {}
        try: c_list = json.loads(c_list) if c_list else []
        except: c_list = []
        try: r_list = json.loads(r_list) if r_list else []
        except: r_list = []
        
        db[uname] = {
            "password": pwd, "rol": rol, "semestre": sem, "carrera": car,
            "cash": cash, "presupuesto_inicial": p_ini, "portfolio_acciones": p_acc,
            "cdt_list": c_list, "renta_fija_list": r_list, "informe_estudiante": inf, "esg_fund": esg
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
        json.dumps(udata.get("renta_fija_list")), json.dumps([]),
        udata.get("informe_estudiante"), udata.get("esg_fund")
    ))
    conn.commit()
    conn.close()

if "user_database" not in st.session_state:
    st.session_state.user_database = load_user_db_cached()

if "stocks_initialized" not in st.session_state:
    st.session_state.prices = {
        "ECOPETROL": 2685, "BCOLOMBIA": 33500, "ISA": 18900, "GRUPOSURA": 36200, "NUTRESA": 46000
    }
    st.session_state.stocks_initialized = True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# LOGIN
# ==========================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
            <div style="background: rgba(13, 20, 36, 0.85); border: 1px solid rgba(88, 166, 255, 0.3); border-radius: 24px; padding: 40px; width: 100%; max-width: 450px;">
                <h1 style="text-align: center; color: #58a6ff;">🔐 BCV By Jp</h1>
                <h3 style="text-align: center; color: #8b949e; font-size: 1rem;">Terminal Financiera Unisucre</h3>
        """, unsafe_allow_html=True
    )
    with st.form("form_login"):
        user_input = st.text_input("Nombre de Usuario:")
        pass_input = st.text_input("Contraseña:", type="password")
        if st.form_submit_button("Ingresar al Portal 🚀"):
            if user_input.strip() and pass_input.strip():
                if user_input not in st.session_state.user_database:
                    st.session_state.user_database[user_input] = {
                        "password": pass_input, "rol": "Estudiante", "semestre": "Semestre 5",
                        "carrera": "Administración de Empresas", "cash": 500000, "presupuesto_inicial": 500000,
                        "portfolio_acciones": {}, "cdt_list": [], "renta_fija_list": [],
                        "informe_estudiante": "", "esg_fund": 0
                    }
                    save_user_to_db(user_input, st.session_state.user_database[user_input])
                st.session_state.current_user = user_input
                st.session_state.logged_in = True
                st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

usuario_activo = st.session_state.current_user
u_data = st.session_state.user_database[usuario_activo]

# ==========================================
# CÓDIGO DEL BANNER DE JP EN TODAS LAS PÁGINAS
# ==========================================
def render_guia_banner_global():
    has_img = os.path.exists("jp_foto.jpg")
    img_html = ""
    if has_img:
        with open("jp_foto.jpg", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_html = f'<img src="data:image/jpeg;base64,{img_b64}" class="jp-avatar-img" />'
    else:
        img_html = '<div style="font-size: 3.5rem;">👨‍💼</div>'

    st.markdown(
        f"""
        <div class="jp-global-banner">
            <div>{img_html}</div>
            <div style="flex-grow: 1;">
                <h3 style="color: #facc15; margin: 0; font-size: 1.4rem;">🟡 Jp - Tu Guía Virtual Unisucre</h3>
                <p style="color: #e2e8f0; margin: 5px 0 0 0; font-size: 0.95rem;">
                    ¡Habla, <b>{usuario_activo}</b>! Bienvenido a la terminal. Recuerda revisar la sección de <b>Introducción a la BVC</b> para aprender a dominar el mercado colombiano.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# SIDEBAR NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.title("📈 BCV By Jp")
    st.success(f"👤 **{usuario_activo}**")
    
    menu = option_menu(
        "Navegación Principal",
        ["Introducción BVC", "Terminal Bursátil", "Catálogo Técnico", "CDT y Bonos", "Fondo ESG"],
        icons=["book-half", "cart", "graph-up", "bank", "tree"],
        menu_icon="compass", default_index=0
    )

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

# MOSTRAR EL GUÍA JP EN ABSOLUTAMENTE TODAS LAS VISTAS
render_guia_banner_global()

# ==========================================
# MÓDULO: INTRODUCCIÓN ATRACTIVA A LA BVC
# ==========================================
if menu == "Introducción BVC":
    st.title("🇨🇴 Todo lo que debes saber sobre la Bolsa de Valores de Colombia (BVC)")
    st.caption("Aprende a operar como un profesional del mercado colombiano con la guía de Jp.")

    st.markdown(
        """
        <div class="asset-card">
            <h2>🔥 ¿Qué es la BVC y cómo funciona?</h2>
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Imagina la <b>Bolsa de Valores de Colombia (BVC)</b> como el mercado más grande y seguro del país, pero en vez de comprar y vender yuca o suero, 
                aquí se negocian <b>partes de las empresas más potentes de Colombia</b> (Ecopetrol, Bancolombia, ISA) y <b>deuda pública del Estado (TES)</b>.
            </p>
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Su función principal es conectar a las empresas que necesitan dinero para financiar sus proyectos con las personas o instituciones que tienen capital ahorrado y quieren rentabilizarlo.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="asset-card" style="min-height: 280px;">
                <h3>📈 1. Renta Variable (Acciones)</h3>
                <p>Te convierte en <b>socio copropietario</b> de la empresa.</p>
                <ul>
                    <li><b>Ganancia por Valorización:</b> Si la empresa crece, la acción sube de precio.</li>
                    <li><b>Dividendos:</b> Reparto periódico de las utilidades fijado por la asamblea.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="asset-card" style="min-height: 280px;">
                <h3>📜 2. Renta Fija (TES y Bonos)</h3>
                <p>Le prestas tu dinero al Estado o a empresas corporativas.</p>
                <ul>
                    <li><b>Rendimiento Seguro:</b> Conoces de antemano la tasa de interés (E.A.).</li>
                    <li><b>Bajo Riesgo:</b> Ideal para proteger el capital contra la inflación.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="asset-card" style="min-height: 280px;">
                <h3>🇨🇴 3. El Índice COLCAP</h3>
                <p>El termómetro oficial de la bolsa colombiana.</p>
                <ul>
                    <li>Mide el comportamiento de las <b>20 acciones más líquidas y transadas</b> del país.</li>
                    <li>Si el COLCAP sube, indica salud y confianza económica en Colombia.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("### 📊 Principales Activos que Vas a Operar en este Simulador")
    df_activos = pd.DataFrame([
        {"Ticker": "ECOPETROL", "Sector": "Energético / Petróleo", "Por qué operar": "Empresa insignia de Colombia, destaca por pagar dividendos atractivos."},
        {"Ticker": "BCOLOMBIA", "Sector": "Financiero", "Por qué operar": "Líder del sistema bancario, con presencia masiva en todo el país."},
        {"Ticker": "ISA", "Sector": "Infraestructura / Energía", "Por qué operar": "Flujos de caja muy estables por contratos de transmisión de energía a largo plazo."},
        {"Ticker": "GRUPOSURA", "Sector": "Holding / Inversiones", "Por qué operar": "Diversificación en servicios financieros, pensiones y seguros en Latinoamérica."}
    ])
    st.table(df_activos)

elif menu == "Terminal Bursátil":
    st.title("🛒 Terminal Bursátil de Compra y Venta")
    st.success("Aquí puedes aplicar lo aprendido e invertir tus $500,000 COP iniciales.")

elif menu == "Catálogo Técnico":
    st.title("📊 Catálogo Técnico de Activos")
    st.info("Revisa las tendencias de precios en tiempo real.")

elif menu == "CDT y Bonos":
    st.title("🏦 Renta Fija: CDT y Bonos Soberanos")
    st.info("Asegura tasas fijas con riesgo mínimo.")

elif menu == "Fondo ESG":
    st.title("🌱 Fondo Sostenible ESG")
    st.info("Invierta en empresas con alto impacto ambiental y social.")