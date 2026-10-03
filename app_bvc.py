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

# Configuración general de la página
st.set_page_config(
    page_title="BCV By Jp - Terminal Financiera Unisucre",
    page_icon="📈",
    layout="wide",
)

# ==========================================
# ESTILOS CSS CON EFECTOS NEÓN MULTICOLOR + GLASSMORPHISM
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
        font-size: 1.25rem;
    }

    body {
        background: 
            linear-gradient(rgba(4, 8, 18, 0.88), rgba(4, 8, 18, 0.95)),
            url("fondo-financiero.jpg") center/cover no-repeat fixed;
    }

    /* Banner Global de Jp en la parte superior con Neón Dorado */
    .jp-global-banner {
        background: linear-gradient(135deg, rgba(13, 27, 42, 0.9) 0%, rgba(27, 38, 59, 0.9) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 2px solid #facc15;
        border-radius: 20px;
        padding: 18px 25px;
        margin-bottom: 25px;
        box-shadow: 0 0 25px rgba(250, 204, 21, 0.35);
        display: flex;
        align-items: center;
        gap: 20px;
        transition: all 0.3s ease;
    }
    .jp-global-banner:hover {
        box-shadow: 0 0 35px rgba(250, 204, 21, 0.6);
        border-color: #ffe066;
    }

    .jp-avatar-img {
        width: 85px;
        height: 85px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #facc15;
        box-shadow: 0 0 20px rgba(250, 204, 21, 0.6);
        animation: floatJp 3.5s ease-in-out infinite;
    }

    /* Hero de Masterclass Jp en Pantalla Gigante */
    .hero-jp-masterclass {
        background: radial-gradient(circle at top center, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 2px solid #facc15;
        border-radius: 28px;
        padding: 45px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 55px rgba(250, 204, 21, 0.35), inset 0 0 25px rgba(250, 204, 21, 0.15);
    }

    .jp-masterclass-img {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #facc15;
        box-shadow: 0 0 40px rgba(250, 204, 21, 0.7);
        margin-bottom: 18px;
        animation: floatJp 3.5s ease-in-out infinite;
    }

    @keyframes floatJp {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-7px) scale(1.02); }
        100% { transform: translateY(0px) scale(1); }
    }

    /* Tarjetas Genéricas y Neón */
    .neon-card {
        background: linear-gradient(135deg, rgba(16, 22, 34, 0.85) 0%, rgba(26, 34, 51, 0.85) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(88, 166, 255, 0.35);
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5), 0 0 15px rgba(56, 189, 248, 0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .neon-card:hover {
        transform: translateY(-7px);
        border-color: #38bdf8;
        box-shadow: 0 15px 35px rgba(56, 189, 248, 0.35), 0 0 25px rgba(56, 189, 248, 0.25);
    }

    /* TARJETAS NEÓN TRII POR COLORES SECTORIALES */
    .trii-card-blue {
        background: linear-gradient(135deg, rgba(10, 25, 47, 0.9) 0%, rgba(15, 30, 55, 0.9) 100%);
        border: 1px solid #38bdf8;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
        transition: all 0.3s ease;
    }
    .trii-card-blue:hover {
        transform: translateY(-6px);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.45);
        border-color: #7dd3fc;
    }

    .trii-card-gold {
        background: linear-gradient(135deg, rgba(30, 25, 10, 0.9) 0%, rgba(45, 35, 15, 0.9) 100%);
        border: 1px solid #facc15;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(250, 204, 21, 0.2);
        transition: all 0.3s ease;
    }
    .trii-card-gold:hover {
        transform: translateY(-6px);
        box-shadow: 0 0 30px rgba(250, 204, 21, 0.45);
        border-color: #fde047;
    }

    .trii-card-green {
        background: linear-gradient(135deg, rgba(6, 32, 18, 0.9) 0%, rgba(13, 48, 26, 0.9) 100%);
        border: 1px solid #2ea043;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(46, 160, 67, 0.2);
        transition: all 0.3s ease;
    }
    .trii-card-green:hover {
        transform: translateY(-6px);
        box-shadow: 0 0 30px rgba(46, 160, 67, 0.45);
        border-color: #4ade80;
    }

    .trii-card-purple {
        background: linear-gradient(135deg, rgba(28, 15, 45, 0.9) 0%, rgba(40, 20, 65, 0.9) 100%);
        border: 1px solid #c084fc;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(192, 132, 252, 0.2);
        transition: all 0.3s ease;
    }
    .trii-card-purple:hover {
        transform: translateY(-6px);
        box-shadow: 0 0 30px rgba(192, 132, 252, 0.45);
        border-color: #e9d5ff;
    }

    .concept-badge {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 5px 14px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 12px;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
    }

    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# BASE DE DATOS Y PERSISTENCIA (SQLITE)
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

# ==========================================
# DICCIONARIO MAESTRO DE LAS 36 ACCIONES BVC / TRII
# ==========================================
bvc_36_actions_master = {
    "ECOPETROL": {"precio": 2685, "logo": "🛢️", "sector": "Petróleo y Gas", "color": "blue", "desc": "Empresa petrolera oficial de Colombia. Explora, refina y transporta hidrocarburos."},
    "BCOLOMBIA": {"precio": 33500, "logo": "🏦", "sector": "Financiero", "color": "gold", "desc": "El banco comercial más grande del país con operación en toda Latinoamérica."},
    "PFBCOLOMB": {"precio": 31200, "logo": "💳", "sector": "Financiero", "color": "gold", "desc": "Acción preferencial sin derecho a voto de Bancolombia."},
    "ISA": {"precio": 18900, "logo": "⚡", "sector": "Energía / Infraestructura", "color": "blue", "desc": "Transporta más del 70% de la energía eléctrica en Colombia y la región."},
    "GRUPOSURA": {"precio": 36200, "logo": "📈", "sector": "Holding Financiero", "color": "gold", "desc": "Holding multinacional enfocado en banca, seguros, pensiones y servicios."},
    "PFGRUPSURA": {"precio": 28400, "logo": "📊", "sector": "Holding Financiero", "color": "gold", "desc": "Título preferencial de Grupo Sura con dividendo prioritario."},
    "CELSIA": {"precio": 4250, "logo": "💡", "sector": "Energía Renovables", "color": "blue", "desc": "Generación y distribución de energías limpias (solar, eólica e hídrica)."},
    "CEMARGOS": {"precio": 7800, "logo": "🏗️", "sector": "Materiales / Construcción", "color": "green", "desc": "Líder en producción y comercialización de cemento y concreto en las Américas."},
    "PFCEMARGOS": {"precio": 6100, "logo": "🧱", "sector": "Materiales / Construcción", "color": "green", "desc": "Acción preferencial de Cementos Argos S.A."},
    "GRUPOARGOS": {"precio": 14200, "logo": "🏙️", "sector": "Holding Infraestructura", "color": "green", "desc": "Holding de infraestructura, concesiones viales, aeropuertos y cementos."},
    "PFGRUPOARG": {"precio": 10500, "logo": "🏛️", "sector": "Holding Infraestructura", "color": "green", "desc": "Acción preferencial de Grupo Argos."},
    "NUTRESA": {"precio": 46000, "logo": "🍫", "sector": "Alimentos Procesados", "color": "purple", "desc": "Gigante multilatina procesadora de chocolates, galletas, carnes y cafés."},
    "PROMIGAS": {"precio": 6400, "logo": "🔥", "sector": "Gas Natural", "color": "blue", "desc": "Transporte y distribución masiva de gas natural en Colombia y Perú."},
    "CORFICOLCF": {"precio": 19800, "logo": "💼", "sector": "Corporación Financiera", "color": "gold", "desc": "Inversión en megaproyectos viales, infraestructura energética y banca."},
    "PFDAVVNDA": {"precio": 27200, "logo": "🏛️", "sector": "Banca Comercial", "color": "gold", "desc": "Acción preferencial de Banco Davivienda y plataforma Daviplata."},
    "BOGOTA": {"precio": 35000, "logo": "🏬", "sector": "Financiero", "color": "gold", "desc": "Banco de Bogotá, una de las instituciones bancarias más antiguas de Colombia."},
    "PFAVAL": {"precio": 535, "logo": "📉", "sector": "Holding Bancario", "color": "gold", "desc": "Grupo Aval, conglomerado dueño de Banco de Bogotá, Occidente y Porvenir."},
    "MINEROS": {"precio": 3950, "logo": "⛏️", "sector": "Minería de Oro", "color": "green", "desc": "Exploración y producción responsable de oro en Colombia y Argentina."},
    "ETB": {"precio": 185, "logo": "☎️", "sector": "Telecomunicaciones", "color": "purple", "desc": "Empresa de Telecomunicaciones de Bogotá, red de fibra óptica y servicios digital."},
    "GEB": {"precio": 2450, "logo": "🔌", "sector": "Energía de Bogotá", "color": "blue", "desc": "Grupo Energía Bogotá, transmisión y distribución de electricidad y gas."},
    "TERPEL": {"precio": 8900, "logo": "⛽", "sector": "Combustibles", "color": "purple", "desc": "Red de estaciones de servicio y distribución de lubricantes y combustibles."},
    "ELCONDOR": {"precio": 1150, "logo": "🚜", "sector": "Construcción e Infraestructura", "color": "green", "desc": "Construcción de vías de cuarta generación (4G) e ingeniería civil."},
    "CLH": {"precio": 3200, "logo": "🏗️", "sector": "Cementos", "color": "green", "desc": "Cemex Latam Holdings, producción de materiales de construcción."},
    "CONCONCRET": {"precio": 280, "logo": "🛠️", "sector": "Construcción", "color": "green", "desc": "Constructora Conconcreto S.A., edificaciones e infraestructura masiva."},
    "ENKA": {"precio": 22, "logo": "🧵", "sector": "Textil y Reciclaje PET", "color": "purple", "desc": "Transformación de botellas recicladas en resinas y hilos sintéticos."},
    "BVC": {"precio": 11200, "logo": "🔔", "sector": "Bolsa / Financiero", "color": "gold", "desc": "La propia empresa administradora del mercado de valores de Colombia."},
    "PEI": {"precio": 68000, "logo": "🏢", "sector": "Real Estate / Inmobiliario", "color": "purple", "desc": "Fondo de inversión inmobiliario en centros comerciales, oficinas y bodegas."},
    "FABRICATO": {"precio": 6, "logo": "👕", "sector": "Textil", "color": "purple", "desc": "Compañía textilera colombiana procesadora de telas y confecciones."},
    "AVIANCA": {"precio": 45, "logo": "✈️", "sector": "Aerolíneas", "color": "purple", "desc": "Línea aérea insignia de transporte de pasajeros y carga."},
    "POPULAR": {"precio": 280, "logo": "🏦", "sector": "Banca", "color": "gold", "desc": "Banco Popular Colombia, filial de Grupo Aval especializada en crédito bancario."},
    "OCCIDENTE": {"precio": 32000, "logo": "🏧", "sector": "Banca", "color": "gold", "desc": "Banco de Occidente, soluciones financieras corporativas y personales."},
    "CANCHAM": {"precio": 1500, "logo": "🌾", "sector": "Agroindustria", "color": "green", "desc": "Desarrollo de proyectos agrícolas y procesamiento agroindustrial."},
    "CARTON": {"precio": 8500, "logo": "📦", "sector": "Empaques / Cartón", "color": "purple", "desc": "Smurfit Kappa Cartón de Colombia, fabricación de empaques de papel."},
    "COLTEJER": {"precio": 12, "logo": "🧵", "sector": "Textiles", "color": "purple", "desc": "Compañía Colombiana de Tejidos fundada en Medellín."},
    "PFCORFICOL": {"precio": 16500, "logo": "💼", "sector": "Corporación Financiera", "color": "gold", "desc": "Acción preferencial de Corficolombiana."},
    "PFCELSA": {"precio": 3900, "logo": "💡", "sector": "Energía", "color": "blue", "desc": "Acción preferencial de Celsia S.A."}
}

# ==========================================
# DICCIONARIO MAESTRO DE FONDOS DE INVERSIÓN (FICs / trii)
# ==========================================
trii_fics_master = {
    "FIC_ACCIONES": {"nombre": "trii Acciones Colombia", "gestor": "Acciones & Valores S.A.", "rentabilidad_ea": "14.2% E.A.", "riesgo": "Alto", "logo": "🚀", "color": "blue", "desc": "Fondo enfocado en la canasta del índice MSCI COLCAP y las mejores acciones de la BVC."},
    "FIC_RENTA_FIJA": {"nombre": "trii Renta Fija Liquidez", "gestor": "Acciones & Valores S.A.", "rentabilidad_ea": "10.8% E.A.", "riesgo": "Bajo", "logo": "🛡️", "color": "green", "desc": "Fondo de liquidez invertido en TES del gobierno y CDTs bancarios de alta calificación."},
    "FIC_ACCIVAL_VISTA": {"nombre": "Accival Vista Liquidez", "gestor": "Acciones & Valores S.A.", "rentabilidad_ea": "11.1% E.A.", "riesgo": "Bajo", "logo": "💧", "color": "green", "desc": "Fondo vista de alta seguridad y disponibilidad diaria de capital para perfiles conservadores."},
    "FIC_GLOBAL": {"nombre": "trii Global / Tech ETF", "gestor": "Acciones & Valores S.A.", "rentabilidad_ea": "16.5% E.A.", "riesgo": "Moderado-Alto", "logo": "🌐", "color": "purple", "desc": "Diversificación en dólares e inversión en las empresas tecnológicas más grandes del mundo."},
    "FIC_INMOBILIARIO": {"nombre": "trii Renta Inmobiliaria", "gestor": "Acciones & Valores S.A.", "rentabilidad_ea": "12.0% E.A.", "riesgo": "Moderado", "logo": "🏢", "color": "gold", "desc": "Inversión colectiva en inmuebles comerciales, logísticos y de oficinas de alta rentabilidad."},
    "FIC_SOSTENIBLE": {"nombre": "trii Sostenible ESG", "gestor": "Acciones & Valores S.A.", "rentabilidad_ea": "13.1% E.A.", "riesgo": "Moderado", "logo": "🌱", "color": "green", "desc": "Portafolio enfocado exclusivamente en empresas con altos estándares ambientales y sociales."}
}

st.session_state.prices_dict = bvc_36_actions_master
if "prices" not in st.session_state or len(st.session_state.prices) < 36:
    st.session_state.prices = {k: v["precio"] for k, v in bvc_36_actions_master.items()}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# LOGIN
# ==========================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
            <div style="background: rgba(13, 20, 36, 0.85); border: 1px solid rgba(88, 166, 255, 0.4); border-radius: 24px; padding: 40px; width: 100%; max-width: 450px; box-shadow: 0 0 35px rgba(88, 166, 255, 0.2);">
                <h1 style="text-align: center; color: #58a6ff;">🔐 BCV By Jp</h1>
                <h3 style="text-align: center; color: #8b949e; font-size: 1rem;">Terminal Financiera Unisucre</h3>
        """, unsafe_allow_html=True
    )
    with st.form("form_login"):
        user_input = st.text_input("Nombre Completo:")
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
# BANNER GLOBAL DE JP
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
                <h3 style="color: #facc15; margin: 0; font-size: 1.35rem; text-shadow: 0 0 10px rgba(250, 204, 21, 0.4);">🟡 Jp - Tu Guía Virtual Unisucre</h3>
                <p style="color: #e2e8f0; margin: 4px 0 0 0; font-size: 0.95rem;">
                    ¡Epa, <b>{usuario_activo}</b>! Bienvenido a la plataforma. Revisa la <b>Masterclass de Jp</b> para aprender por qué invertir es la clave de tu futuro.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.title("📈 BCV By Jp")
    st.success(f"👤 **{usuario_activo}**")
    
    menu = option_menu(
        "Navegación Principal",
        ["Masterclass BVC con Jp", "Terminal Bursátil", "Fondos de Inversión (trii)", "Simulador Proyectivo", "CDT y Bonos", "Fondo ESG"],
        icons=["camera-reels", "cart", "layers", "calculator", "bank", "tree"],
        menu_icon="compass", default_index=0
    )

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

render_guia_banner_global()

# ==========================================
# MASTERCLASS DE JP (INTACTA CON NEON)
# ==========================================
if menu == "Masterclass BVC con Jp":
    has_img = os.path.exists("jp_foto.jpg")
    img_hero_html = ""
    if has_img:
        with open("jp_foto.jpg", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_hero_html = f'<img src="data:image/jpeg;base64,{img_b64}" class="jp-masterclass-img" />'
    else:
        img_hero_html = '<div style="font-size: 6rem;">👨‍💼</div>'

    st.markdown(
        f"""
        <div class="hero-jp-masterclass">
            {img_hero_html}
            <h1 style="color: #facc15; font-size: 2.6rem; margin-bottom: 8px; text-shadow: 0 0 20px rgba(250, 204, 21, 0.5);">🎓 Masterclass de Inversión y Bolsa de Valores (BVC)</h1>
            <h3 style="color: #94a3b8; font-weight: 400; margin-bottom: 15px; font-size: 1.2rem;">
                Dictado por <b>Juan Pablo López Tarriba (Jp)</b> | Universidad de Sucre
            </h3>
            <p style="font-size: 1.15rem; color: #cbd5e1; max-width: 880px; margin: 0 auto; line-height: 1.7;">
                ¡Habla, cuadro! Esta guía fue creada para romper el mito de que <i>"la bolsa es solo para ricos"</i> y darte las herramientas reales para administrar con inteligencia tu saldo inicial de <b>$500.000 COP</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_m1, tab_m2, tab_m3, tab_m4, tab_m5 = st.tabs([
        "💡 1. ¿Por qué Invertir?",
        "🏛 2. ¿Qué es la BVC?",
        "⚖️ 3. Renta Variable vs. Renta Fija",
        "🌎 4. Casos Reales de Éxito",
        "🧠 5. Mente de Inversionista"
    ])

    with tab_m1:
        st.markdown(
            """
            <div class="neon-card">
                <span class="concept-badge">El Despertar Financiero</span>
                <h2 style="margin-top: 5px;">🔥 ¿Por qué Invertir no es Opcional?</h2>
                <p style="font-size: 1.05rem; line-height: 1.8; color: #e2e8f0;">
                    Mucha gente cree que ahorrar dinero en una cuenta tradicional o debajo del colchón es seguro. <b>¡Gran error!</b> Existe un enemigo silencioso llamado <b>INFLACIÓN</b>. 
                    Si la inflación en Colombia es del 7% anual y tu dinero guardado te da el 1%, en realidad <b>estás perdiendo un 6% de poder de compra cada año</b>.
                </p>
            </div>
            <div class="neon-card-green">
                <h3 style="color: #2ea043; margin-top: 0; text-shadow: 0 0 10px rgba(46, 160, 67, 0.4);">✨ El Secreto del Interés Compuesto (La 8ª Maravilla del Mundo)</h3>
                <p style="font-size: 1.02rem; line-height: 1.8; color: #e2e8f0;">
                    Albert Einstein decía que el interés compuesto es la fuerza más poderosa del universo. Consiste en reinvertir las ganancias generadas para que tus intereses generen más intereses. 
                    Si inviertes $500.000 COP hoy con un retorno promedio del 12% anual y reinviertes tus ganancias, ¡tu dinero trabajará para ti de forma exponencial!
                </p>
            </div>
            """, unsafe_allow_html=True
        )

    with tab_m2:
        st.markdown(
            """
            <div class="neon-card">
                <span class="concept-badge">Mecanismo de Mercado</span>
                <h2 style="margin-top: 5px;">🏛️️ ¿Qué es la BVC y cuál es su Rol en Colombia?</h2>
                <p style="font-size: 1.05rem; line-height: 1.8; color: #e2e8f0;">
                    La <b>Bolsa de Valores de Colombia (BVC)</b> es la plaza de mercado oficial donde se conectan las empresas que necesitan capital para crecer con las personas e instituciones que tienen ahorros disponibles.
                </p>
            </div>
            """, unsafe_allow_html=True
        )

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(
                """
                <div class="neon-card" style="min-height: 200px;">
                    <h4 style="color: #38bdf8;">🏢 Empresas (Deficitarios)</h4>
                    <p style="color: #cbd5e1; font-size: 0.98rem;">Emiten acciones o bonos para construir infraestructura, expandir plantas y crear empleo sin endeudarse únicamente con bancos.</p>
                </div>
                """, unsafe_allow_html=True
            )
        with col_c2:
            st.markdown(
                """
                <div class="neon-card" style="min-height: 200px;">
                    <h4 style="color: #38bdf8;">💼 Inversionistas (Superavitarios)</h4>
                    <p style="color: #cbd5e1; font-size: 0.98rem;">Aportan capital a proyectos productivos a cambio de rentabilidades superiores a las de los métodos de ahorro tradicionales.</p>
                </div>
                """, unsafe_allow_html=True
            )

        st.markdown(
            """
            <div class="neon-card-green">
                <h4 style="color: #2ea043; margin-top: 0;">🛡️ Seguridad Garantizada</h4>
                <p style="color: #e2e8f0; margin-bottom: 0;">El mercado de valores colombiano está rigurosamente vigilado por la <b>Superintendencia Financiera de Colombia (SFC)</b> y el <b>Autoregulador del Mercado de Valores (AMV)</b>.</p>
            </div>
            """, unsafe_allow_html=True
        )

    with tab_m3:
        col_rv, col_rf = st.columns(2)
        with col_rv:
            st.markdown(
                """
                <div class="neon-card" style="min-height: 380px;">
                    <span class="concept-badge">Crecimiento / Mayor Retorno</span>
                    <h3 style="color: #58a6ff; margin-top: 5px;">📈 Renta Variable (Acciones)</h3>
                    <p style="color: #e2e8f0;">Te convierte en <b>socio copropietario</b> de empresas como Ecopetrol o Bancolombia.</p>
                    <ul style="color: #cbd5e1; line-height: 1.8;">
                        <li><b>Valorización:</b> La acción sube de precio si la empresa crece.</li>
                        <li><b>Dividendos:</b> Reparto periódico de utilidades generadas en efectivo.</li>
                    </ul>
                    <p style="color: #f87171; font-size: 0.88rem; margin-top: 15px;">⚠️ <i>Requiere tolerancia a las oscilaciones diarias de mercado.</i></p>
                </div>
                """, unsafe_allow_html=True
            )
        with col_rf:
            st.markdown(
                """
                <div class="neon-card" style="min-height: 380px;">
                    <span class="concept-badge">Estabilidad y Protección</span>
                    <h3 style="color: #2ea043; margin-top: 5px;">📜 Renta Fija (TES y CDT)</h3>
                    <p style="color: #e2e8f0;">Te convierte en <b>prestamista</b> del Estado Colombiano o de bancos de primer nivel.</p>
                    <ul style="color: #cbd5e1; line-height: 1.8;">
                        <li><b>Intereses Conocidos:</b> Tasa pactada desde el primer día (ej. 11.5% E.A.).</li>
                        <li><b>Riesgo Mínimo:</b> Respaldados por la Nación o el seguro de depósito FOGAFIN.</li>
                    </ul>
                    <p style="color: #38bdf8; font-size: 0.88rem; margin-top: 15px;">💡 <i>Ideal para armar la base segura de tu portafolio.</i></p>
                </div>
                """, unsafe_allow_html=True
            )

    with tab_m4:
        st.subheader("🌎 Casos Reales: Lo que nos Enseña la Historia")
        st.caption("Lecciones con Historia")
        
        st.markdown(
            """
            <div class="neon-card">
                <h4 style="color: #facc15; font-size: 1.2rem; margin-top: 0;">🌟 Caso 1: Anne Scheiber (El Poder de la Disciplina)</h4>
                <p style="color: #cbd5e1; line-height: 1.7; font-size: 0.98rem;">
                    Anne era una auditora estadounidense con un salario modesto. Durante más de 50 años invirtió disciplinadamente pequeñas sumas en acciones de empresas sólidas y nunca vendió en momentos de pánico. 
                    Transformó unos pocos miles de dólares en un patrimonio de <b>más de $22 millones de dólares</b>.
                </p>
            </div>
            <div class="neon-card">
                <h4 style="color: #58a6ff; font-size: 1.2rem; margin-top: 0;">🇨🇴 Caso 2: Dividendos en Colombia (Ecopetrol y Bancolombia)</h4>
                <p style="color: #cbd5e1; line-height: 1.7; font-size: 0.98rem;">
                    Inversionistas en Colombia que compraron acciones de Ecopetrol o Bancolombia durante momentos de crisis y mantuvieron sus posiciones, han recibido <b>retornos anuales en dividendos del 10% al 15% sobre su inversión inicial</b>.
                </p>
            </div>
            """, unsafe_allow_html=True
        )

    with tab_m5:
        st.markdown(
            """
            <div class="neon-card">
                <span class="concept-badge">Mentalidad Unisucre</span>
                <h2 style="margin-top: 5px;">🧠 Las 4 Reglas de Oro de Jp</h2>
                <p style="color: #e2e8f0; font-size: 1.05rem;">Para triunfar en este simulador y en la vida real, aplica estas reglas antes de tocar tus $500.000 COP:</p>
            </div>
            """, unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                """
                <div class="neon-card">
                    <h4 style="color: #facc15;">1. Nunca Inviertas a Ciegas</h4>
                    <p style="color: #cbd5e1;">Conoce el activo, la rentabilidad y el sector de la empresa antes de comprar.</p>
                </div>
                <div class="neon-card">
                    <h4 style="color: #38bdf8;">2. Diversifica sin Miedo</h4>
                    <p style="color: #cbd5e1;">Combina acciones de varios sectores con instrumentos de renta fija (CDT y Bonos).</p>
                </div>
                """, unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                """
                <div class="neon-card">
                    <h4 style="color: #f87171;">3. Controla las Emociones</h4>
                    <p style="color: #cbd5e1;">No compres por euforia en los picos altos ni vendas con pánico en las caídas de mercado.</p>
                </div>
                <div class="neon-card-green">
                    <h4 style="color: #2ea043;">4. Visión a Largo Plazo</h4>
                    <p style="color: #e2e8f0;">La riqueza verdadera en la bolsa se construye con constancia, paciencia e interés compuesto.</p>
                </div>
                """, unsafe_allow_html=True
            )

# ==========================================
# TERMINAL BURSÁTIL (ACCIONES)
# ==========================================
elif menu == "Terminal Bursátil":
    st.title("🛒 Terminal Bursátil: Mercado de Acciones BVC / trii")
    st.caption("36 Activos Oficiales de la Bolsa de Valores de Colombia")

    col_hdr1, col_hdr2 = st.columns([0.7, 0.3])
    with col_hdr1:
        st.write(f"💵 **Efectivo Libre Disponible:** `${u_data['cash']:,.0f} COP`")
    with col_hdr2:
        if st.button("🔄 Actualizar Precios Mercado BVC"):
            for tk in st.session_state.prices:
                var = random.uniform(-0.015, 0.018)
                st.session_state.prices[tk] = max(10, int(st.session_state.prices[tk] * (1 + var)))
            st.success("¡Cotizaciones actualizadas con éxito!")
            st.rerun()

    st.markdown("---")

    items_acciones = list(bvc_36_actions_master.items())
    cols_grid = st.columns(3)

    for idx, (ticker, data_act) in enumerate(items_acciones):
        col_dest = cols_grid[idx % 3]
        prc_actual = st.session_state.prices.get(ticker, data_act["precio"])
        ask_prc = int(prc_actual * 1.002)
        bid_prc = int(prc_actual * 0.998)
        color_class = f"trii-card-{data_act.get('color', 'blue')}"

        with col_dest:
            st.markdown(
                f"""
                <div class="{color_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin:0; font-size: 1.3rem;">{data_act['logo']} {ticker}</h3>
                        <span class="price-tag">${prc_actual:,.0f} COP</span>
                    </div>
                    <p style="color: #94a3b8; font-size: 0.8rem; margin-top:2px;">📌 <b>Sector:</b> {data_act['sector']}</p>
                    <p style="color: #cbd5e1; font-size: 0.9rem; min-height: 50px; line-height:1.4;">
                        {data_act['desc']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander(f"⚡ Operar {ticker}"):
                pos_actual = u_data["portfolio_acciones"].get(ticker, 0)
                st.caption(f"Tienes **{pos_actual}** acciones en tu portafolio.")
                
                tab_comp, tab_vent = st.tabs(["🟢 Comprar", "🔴 Vender"])
                
                with tab_comp:
                    cant_buy = st.number_input(f"Cantidad a comprar ({ticker}):", 1, 100000, 10, key=f"buy_qty_{ticker}")
                    costo_total = ask_prc * cant_buy
                    st.write(f"Costo Total: `${costo_total:,.0f} COP`")
                    if st.button(f"Comprar {ticker}", key=f"btn_buy_{ticker}"):
                        if u_data["cash"] >= costo_total:
                            u_data["cash"] -= costo_total
                            u_data["portfolio_acciones"][ticker] = u_data["portfolio_acciones"].get(ticker, 0) + cant_buy
                            save_user_to_db(usuario_activo, u_data)
                            st.success(f"¡Compraste {cant_buy} títulos de {ticker}!")
                            st.rerun()
                        else:
                            st.error("Efectivo insuficiente.")

                with tab_vent:
                    if pos_actual > 0:
                        cant_sell = st.number_input(f"Cantidad a vender ({ticker}):", 1, pos_actual, 1, key=f"sell_qty_{ticker}")
                        recaudo_total = bid_prc * cant_sell
                        st.write(f"Ingreso Total: `${recaudo_total:,.0f} COP`")
                        if st.button(f"Vender {ticker}", key=f"btn_sell_{ticker}"):
                            u_data["cash"] += recaudo_total
                            u_data["portfolio_acciones"][ticker] -= cant_sell
                            if u_data["portfolio_acciones"][ticker] <= 0:
                                del u_data["portfolio_acciones"][ticker]
                            save_user_to_db(usuario_activo, u_data)
                            st.success(f"¡Vendiste {cant_sell} títulos de {ticker}!")
                            st.rerun()
                    else:
                        st.caption("No posees acciones de esta empresa.")

# ==========================================
# MÓDULO FONDOS DE INVERSIÓN COLECTIVA (trii FICs)
# ==========================================
elif menu == "Fondos de Inversión (trii)":
    st.title("🏦 Fondos de Inversión Colectiva (FICs) - Alianza trii")
    st.caption("Portafolios administrados profesionalmente por Acciones & Valores S.A.")

    st.markdown(
        """
        <div class="neon-card">
            <span class="concept-badge">Gestión Profesional Diversificada</span>
            <h3 style="margin-top: 5px;">💼 Invierte en Fondos Colectivos con un Clic</h3>
            <p style="color: #cbd5e1; line-height: 1.6;">
                Los Fondos de Inversión Colectiva (FICs) te permiten invertir en canastas diversificadas administradas por profesionales. Ideal para combinar rentabilidad y seguridad.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    fics_list = list(trii_fics_master.items())
    cols_fic = st.columns(3)

    for idx, (fic_key, data_fic) in enumerate(fics_list):
        col_f = cols_fic[idx % 3]
        color_f_class = f"trii-card-{data_fic['color']}"

        with col_f:
            st.markdown(
                f"""
                <div class="{color_f_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin:0; font-size: 1.2rem;">{data_fic['logo']} {data_fic['nombre']}</h3>
                    </div>
                    <p style="color: #facc15; font-weight:700; font-size: 1.1rem; margin: 6px 0;">📈 {data_fic['rentabilidad_ea']}</p>
                    <p style="color: #94a3b8; font-size: 0.8rem; margin:0;">🏛️ <b>Gestor:</b> {data_fic['gestor']}</p>
                    <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom:8px;">⚠️ <b>Riesgo:</b> {data_fic['riesgo']}</p>
                    <p style="color: #cbd5e1; font-size: 0.88rem; min-height: 55px; line-height:1.4;">
                        {data_fic['desc']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander(f"📥 Invertir en {data_fic['nombre']}"):
                monto_fic = st.number_input(f"Monto a aportar (COP):", min_value=10000, max_value=int(u_data["cash"] + 1), value=50000, step=10000, key=f"monto_{fic_key}")
                if st.button(f"Suscribir Fondo", key=f"btn_fic_{fic_key}"):
                    if u_data["cash"] >= monto_fic:
                        u_data["cash"] -= monto_fic
                        u_data["esg_fund"] = u_data.get("esg_fund", 0) + monto_fic
                        save_user_to_db(usuario_activo, u_data)
                        st.success(f"¡Suscripción exitosa de ${monto_fic:,.0f} COP en {data_fic['nombre']}!")
                        st.rerun()
                    else:
                        st.error("Efectivo libre insuficiente.")

# ==========================================
# SIMULADOR PROYECTIVO Y ANÁLISIS
# ==========================================
elif menu == "Simulador Proyectivo":
    st.title("🧮 Simulador Proyectivo de Inversión (BVC / Jp)")
    st.caption("Herramienta de simulación de rendimientos futuros con escenarios de mercado")

    st.markdown(
        """
        <div class="neon-card">
            <span class="concept-badge">Laboratorio Financiero Unisucre</span>
            <h3 style="margin-top: 5px;">📊 Simula el Rendimiento Futuro de tu Capital</h3>
            <p style="color: #cbd5e1; line-height: 1.6;">
                Antes de colocar dinero en el mercado real, un buen administrador simula escenarios de retorno basándose en la valorización esperada del activo y el pago histórico de dividendos.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_sim1, col_sim2 = st.columns([0.4, 0.6])

    with col_sim1:
        st.markdown('<div class="neon-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Configuración del Ensayo")
        
        acc_selected = st.selectbox(
            "Selecciona la Acción a Simular:",
            list(bvc_36_actions_master.keys())
        )
        
        info_sim = bvc_36_actions_master[acc_selected]
        prc_sim = st.session_state.prices.get(acc_selected, info_sim["precio"])

        monto_inv = st.number_input(
            "Monto de Inversión Simulado (COP):",
            min_value=50000, max_value=50000000, value=500000, step=50000
        )

        plazo_meses = st.slider("Plazo de Inversión (Meses):", 1, 36, 12)

        st.markdown("---")
        st.caption(f"📌 **{info_sim['logo']} {acc_selected}** | Precio Actual: **${prc_sim:,.0f} COP**")
        st.caption(f"ℹ️ {info_sim['desc']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_sim2:
        tasa_mod = (1 + 0.125)**(plazo_meses/12) - 1
        tasa_opt = (1 + 0.220)**(plazo_meses/12) - 1
        tasa_pes = (1 - 0.050)**(plazo_meses/12) - 1

        val_mod = monto_inv * (1 + tasa_mod)
        val_opt = monto_inv * (1 + tasa_opt)
        val_pes = monto_inv * (1 + tasa_pes)

        st.subheader("🔮 Resultados de la Proyección")

        res_c1, res_c2, res_c3 = st.columns(3)
        with res_c1:
            st.metric("Escenario Moderado", f"${val_mod:,.0f} COP", f"+{tasa_mod*100:.1f}%")
        with res_c2:
            st.metric("Escenario Optimista", f"${val_opt:,.0f} COP", f"+{tasa_opt*100:.1f}%")
        with res_c3:
            st.metric("Escenario Pesimista", f"${val_pes:,.0f} COP", f"{tasa_pes*100:.1f}%", delta_color="inverse")

        meses_eje = list(range(0, plazo_meses + 1))
        curve_mod = [monto_inv * ((1 + 0.125)**(m/12)) for m in meses_eje]
        curve_opt = [monto_inv * ((1 + 0.220)**(m/12)) for m in meses_eje]
        curve_pes = [monto_inv * ((1 - 0.050)**(m/12)) for m in meses_eje]

        df_chart = pd.DataFrame({
            "Mes": meses_eje,
            "Moderado (Promedio)": curve_mod,
            "Optimista (Alcista)": curve_opt,
            "Pesimista (Corrección)": curve_pes
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_chart["Mes"], y=df_chart["Optimista (Alcista)"], name="Optimista", line=dict(color='#2ea043', width=3)))
        fig.add_trace(go.Scatter(x=df_chart["Mes"], y=df_chart["Moderado (Promedio)"], name="Moderado", line=dict(color='#38bdf8', width=3)))
        fig.add_trace(go.Scatter(x=df_chart["Mes"], y=df_chart["Pesimista (Corrección)"], name="Pesimista", line=dict(color='#f87171', width=2, dash='dash')))

        fig.update_layout(
            title=f"Evolución Estimada de ${monto_inv:,.0f} COP en {acc_selected}",
            xaxis_title="Meses de Transcurso",
            yaxis_title="Valor del Capital (COP)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(13, 20, 36, 0.7)',
            font=dict(color='#e2e8f0'),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )

        st.plotly_chart(fig, use_container_width=True)

elif menu == "CDT y Bonos":
    st.title("🏦 Renta Fija: CDT y Bonos Soberanos")
    st.info("Asegura tasas fijas con riesgo mínimo.")

elif menu == "Fondo ESG":
    st.title("🌱 Fondo Sostenible ESG")
    st.info("Invierta en empresas con alto impacto ambiental y social.")