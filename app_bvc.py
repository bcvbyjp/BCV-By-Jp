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
            "cash": cash if cash is not None else 500000.0,
            "presupuesto_inicial": p_ini if p_ini is not None else 500000.0,
            "portfolio_acciones": p_acc,
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
        udata.get("carrera"), udata.get("cash", 500000.0), udata.get("presupuesto_inicial", 500000.0),
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
# CATÁLOGO COMPLETO DE 50 BANCOS Y ENTIDADES PARA CDTs
# ==========================================
bancos_cdt_50 = [
    {"banco": "Bancolombia S.A.", "tasa_ea": 10.5, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏦"},
    {"banco": "Banco Davivienda", "tasa_ea": 10.8, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏛️"},
    {"banco": "Nu Colombia C.F.", "tasa_ea": 12.5, "plazo_dias": 180, "min_inversion": 10000, "logo": "🟣"},
    {"banco": "Lulo Bank S.A.", "tasa_ea": 12.2, "plazo_dias": 180, "min_inversion": 10000, "logo": "🟢"},
    {"banco": "Banco de Bogotá", "tasa_ea": 10.2, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏬"},
    {"banco": "Banco Falabella S.A.", "tasa_ea": 11.5, "plazo_dias": 360, "min_inversion": 50000, "logo": "💳"},
    {"banco": "Scotiabank Colpatria", "tasa_ea": 10.6, "plazo_dias": 360, "min_inversion": 50000, "logo": "🔴"},
    {"banco": "BBVA Colombia", "tasa_ea": 10.4, "plazo_dias": 360, "min_inversion": 50000, "logo": "🌐"},
    {"banco": "Banco Agrario de Colombia", "tasa_ea": 11.0, "plazo_dias": 360, "min_inversion": 50000, "logo": "🌾"},
    {"banco": "Banco de Occidente", "tasa_ea": 10.3, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏧"},
    {"banco": "Banco Popular S.A.", "tasa_ea": 10.7, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏦"},
    {"banco": "Banco AV Villas", "tasa_ea": 10.5, "plazo_dias": 360, "min_inversion": 50000, "logo": "🔴"},
    {"banco": "Banco Itaú Colombia", "tasa_ea": 10.6, "plazo_dias": 360, "min_inversion": 50000, "logo": "🟧"},
    {"banco": "Banco GNB Sudameris", "tasa_ea": 11.1, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏛️"},
    {"banco": "Banco W S.A.", "tasa_ea": 12.8, "plazo_dias": 360, "min_inversion": 50000, "logo": "💼"},
    {"banco": "Banco Caja Social", "tasa_ea": 10.9, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏠"},
    {"banco": "Banco Pichincha Colombia", "tasa_ea": 11.8, "plazo_dias": 360, "min_inversion": 50000, "logo": "🟡"},
    {"banco": "Bancoomeva", "tasa_ea": 11.4, "plazo_dias": 360, "min_inversion": 50000, "logo": "🟢"},
    {"banco": "Financiera Juriscoop", "tasa_ea": 12.1, "plazo_dias": 360, "min_inversion": 50000, "logo": "⚖️️"},
    {"banco": "Banco Serfinanza", "tasa_ea": 11.9, "plazo_dias": 360, "min_inversion": 50000, "logo": "🛒"},
    {"banco": "Tuya C.F.", "tasa_ea": 12.3, "plazo_dias": 180, "min_inversion": 50000, "logo": "🛍️"},
    {"banco": "RCI Colombia S.A.", "tasa_ea": 11.7, "plazo_dias": 360, "min_inversion": 50000, "logo": "🚗"},
    {"banco": "Credifamilia C.F.", "tasa_ea": 12.6, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏡"},
    {"banco": "CFA Coop. Financiera", "tasa_ea": 12.0, "plazo_dias": 360, "min_inversion": 50000, "logo": "🤝"},
    {"banco": "Cotrafa Coop. Financiera", "tasa_ea": 11.9, "plazo_dias": 360, "min_inversion": 50000, "logo": "👥"},
    {"banco": "Confiar Coop. Financiera", "tasa_ea": 11.8, "plazo_dias": 360, "min_inversion": 50000, "logo": "🌱"},
    {"banco": "Financiera Coedenden", "tasa_ea": 12.2, "plazo_dias": 360, "min_inversion": 50000, "logo": "📈"},
    {"banco": "Giros y Finanzas C.F.", "tasa_ea": 11.6, "plazo_dias": 360, "min_inversion": 50000, "logo": "💸"},
    {"banco": "Mibanco S.A.", "tasa_ea": 12.7, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏬"},
    {"banco": "Banco Mundo Mujer", "tasa_ea": 12.9, "plazo_dias": 360, "min_inversion": 50000, "logo": "👩"},
    {"banco": "Coopcentral", "tasa_ea": 11.7, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏦"},
    {"banco": "JPMorgan Chase Colombia", "tasa_ea": 9.8, "plazo_dias": 360, "min_inversion": 100000, "logo": "🏛️"},
    {"banco": "BTG Pactual Colombia", "tasa_ea": 11.2, "plazo_dias": 360, "min_inversion": 50000, "logo": "🌐"},
    {"banco": "Credicorp Bank Colombia", "tasa_ea": 11.0, "plazo_dias": 360, "min_inversion": 50000, "logo": "💼"},
    {"banco": "Citibank Colombia", "tasa_ea": 9.9, "plazo_dias": 360, "min_inversion": 100000, "logo": "🔵"},
    {"banco": "Banco Santander Colombia", "tasa_ea": 10.4, "plazo_dias": 360, "min_inversion": 50000, "logo": "🔴"},
    {"banco": "Finandina Banco Digital", "tasa_ea": 11.8, "plazo_dias": 360, "min_inversion": 50000, "logo": "📱"},
    {"banco": "Irsi C.F.", "tasa_ea": 12.0, "plazo_dias": 360, "min_inversion": 50000, "logo": "📊"},
    {"banco": "Financiera Progresar", "tasa_ea": 12.1, "plazo_dias": 360, "min_inversion": 50000, "logo": "🚀"},
    {"banco": "Coltefinanciera S.A.", "tasa_ea": 12.4, "plazo_dias": 360, "min_inversion": 50000, "logo": "🧵"},
    {"banco": "Danacop Cooperativa", "tasa_ea": 12.2, "plazo_dias": 360, "min_inversion": 50000, "logo": "🤝"},
    {"banco": "Coopfuturo", "tasa_ea": 12.3, "plazo_dias": 360, "min_inversion": 50000, "logo": "🔮"},
    {"banco": "Financiera Comultrasan", "tasa_ea": 12.0, "plazo_dias": 360, "min_inversion": 50000, "logo": "🟡"},
    {"banco": "Cohemprender Financiera", "tasa_ea": 12.5, "plazo_dias": 360, "min_inversion": 50000, "logo": "💡"},
    {"banco": "Banco Coopserp", "tasa_ea": 11.9, "plazo_dias": 360, "min_inversion": 50000, "logo": "👥"},
    {"banco": "Mercantil Colpatria", "tasa_ea": 10.8, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏢"},
    {"banco": "Corficolombiana Private", "tasa_ea": 11.0, "plazo_dias": 360, "min_inversion": 50000, "logo": "💼"},
    {"banco": "Fiduciaria Bancolombia", "tasa_ea": 10.6, "plazo_dias": 360, "min_inversion": 50000, "logo": "📜"},
    {"banco": "Fiduciaria Bogotá S.A.", "tasa_ea": 10.3, "plazo_dias": 360, "min_inversion": 50000, "logo": "🏬"},
    {"banco": "Fiduciaria Davivienda", "tasa_ea": 10.7, "plazo_dias": 360, "min_inversion": 50000, "logo": "🔴"}
]

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
                        "carrera": "Administración de Empresas", "cash": 500000.0, "presupuesto_inicial": 500000.0,
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

# Garantizar $500.000 COP siempre por defecto
if u_data.get("cash") is None:
    u_data["cash"] = 500000.0
    u_data["presupuesto_inicial"] = 500000.0

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
                    ¡Epa, <b>{usuario_activo}</b>! Tienes un saldo libre inicial de <b>$500.000 COP</b> para comprar acciones y constituir CDTs en 50 bancos.
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
    
    val_acciones_total = sum(
        qty * st.session_state.prices.get(tk, bvc_36_actions_master.get(tk, {}).get("precio", 0))
        for tk, qty in u_data.get("portfolio_acciones", {}).items()
    )
    val_cdt_total = sum(c.get("monto", 0) for c in u_data.get("cdt_list", []))
    patrimonio_total = u_data["cash"] + val_acciones_total + val_cdt_total

    st.markdown("### 💼 Tu Patrimonio Total")
    st.markdown(f"<h2 style='color:#2ea043; margin:0;'>${patrimonio_total:,.0f} COP</h2>", unsafe_allow_html=True)
    st.caption(f"💵 Efectivo Libre: `${u_data['cash']:,.0f} COP`")
    st.caption(f"📈 En Acciones: `${val_acciones_total:,.0f} COP`")
    st.caption(f"📜 En CDTs: `${val_cdt_total:,.0f} COP`")

    st.markdown("---")
    menu = option_menu(
        "Navegación Principal",
        ["Masterclass BVC con Jp", "Terminal Bursátil", "CDT Bancarios (50 Bancos)", "Simulador Proyectivo", "Renta Fija y Bonos TES"],
        icons=["camera-reels", "cart", "bank", "calculator", "shield-check"],
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
                <h2 style="margin-top: 5px;">🏛️ ¿Qué es la BVC y cuál es su Rol en Colombia?</h2>
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
# TERMINAL BURSÁTIL CON CÁLCULOS REALES
# ==========================================
elif menu == "Terminal Bursátil":
    st.title("🛒 Terminal Bursátil: Mercado de Acciones BVC")
    st.caption("36 Activos Oficiales de la Bolsa de Valores de Colombia con Valoración Real de Portafolio")

    col_hdr1, col_hdr2 = st.columns([0.7, 0.3])
    with col_hdr1:
        st.write(f"💵 **Efectivo Libre:** `${u_data['cash']:,.0f} COP` | 💰 **Saldo Inicial:** `${u_data['presupuesto_inicial']:,.0f} COP`")
    with col_hdr2:
        if st.button("🔄 Actualizar Precios Mercado BVC"):
            for tk in st.session_state.prices:
                var = random.uniform(-0.015, 0.018)
                st.session_state.prices[tk] = max(10, int(st.session_state.prices[tk] * (1 + var)))
            st.success("¡Cotizaciones actualizadas con éxito!")
            st.rerun()

    st.markdown("### 📊 Estado Actual de tu Portafolio en Acciones")
    if u_data.get("portfolio_acciones"):
        resumen_data = []
        tot_valor_mercado = 0

        for tk_p, cant_p in u_data["portfolio_acciones"].items():
            if cant_p > 0:
                prc_mkt = st.session_state.prices.get(tk_p, bvc_36_actions_master.get(tk_p, {}).get("precio", 0))
                val_mkt = cant_p * prc_mkt
                tot_valor_mercado += val_mkt
                resumen_data.append({
                    "Ticker": tk_p,
                    "Sector": bvc_36_actions_master.get(tk_p, {}).get("sector", "General"),
                    "Cantidad": cant_p,
                    "Precio Mercado": f"${prc_mkt:,.0f} COP",
                    "Valor Total Mercado": f"${val_mkt:,.0f} COP"
                })

        if resumen_data:
            df_port = pd.DataFrame(resumen_data)
            st.dataframe(df_port, use_container_width=True)
            st.success(f"💎 **Valor Total de tu Portafolio de Acciones a Precio de Mercado:** `${tot_valor_mercado:,.0f} COP`")
        else:
            st.info("Aún no tienes acciones en tu portafolio.")
    else:
        st.info("Tu portafolio está vacío. Compra tus primeras acciones abajo.")

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
# MÓDULO: CDT BANCARIOS (50 BANCOS + CALCULADORA INTERÉS COMPUESTO)
# ==========================================
elif menu == "CDT Bancarios (50 Bancos)":
    st.title("🏦 Certificados de Depósito a Término (CDT) en Colombia")
    st.caption("50 Entidades Bancarias con Calculadora de Interés Compuesto Futuro")

    # 🧮 CALCULADORA DE INTERÉS COMPUESTO DE CDTs
    st.markdown(
        """
        <div class="neon-card-green">
            <h3 style="color: #2ea043; margin-top: 0;">🧮 Calculadora de Interés Compuesto Futuro para CDTs</h3>
            <p style="color: #e2e8f0; font-size: 0.95rem;">
                Averigua cuánto crecerá tu capital si dejas tu CDT produciendo intereses y reinviertes tus rendimientos periodo a periodo.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c_calc1, c_calc2 = st.columns([0.4, 0.6])

    with c_calc1:
        st.markdown('<div class="neon-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Parámetros de Inversión")
        monto_c = st.number_input("Monto Inicial a Invertir (COP):", min_value=10000, max_value=100000000, value=500000, step=50000)
        tasa_c = st.number_input("Tasa Efectiva Anual (E.A. %):", min_value=1.0, max_value=30.0, value=12.0, step=0.5)
        anios_c = st.slider("Años de Reinversión Continua:", 1, 10, 3)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_calc2:
        # Fórmula de Interés Compuesto: Vf = Vi * (1 + i)^n
        vf_final = monto_c * ((1 + (tasa_c/100))**anios_c)
        ganancia_neta = vf_final - monto_c

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("Capital Futuro Total", f"${vf_final:,.0f} COP")
        with col_r2:
            st.metric("Intereses Ganados", f"+${ganancia_neta:,.0f} COP", f"+{(ganancia_neta/monto_c)*100:.1f}%")

        # Gráfico Plotly
        eje_anios = list(range(0, anios_c + 1))
        eje_valores = [monto_c * ((1 + (tasa_c/100))**a) for a in eje_anios]

        df_cdt_comp = pd.DataFrame({"Año": eje_anios, "Valor acumulado": eje_valores})
        fig_cdt = px.line(df_cdt_comp, x="Año", y="Valor acumulado", markers=True, title=f"Proyección a {anios_c} Años con {tasa_c}% E.A.")
        fig_cdt.update_traces(line_color='#2ea043', line_width=3)
        fig_cdt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13, 20, 36, 0.7)', font=dict(color='#e2e8f0'))
        st.plotly_chart(fig_cdt, use_container_width=True)

    st.markdown("---")

    # Mostrar CDTs constituidos activos
    if u_data.get("cdt_list"):
        st.subheader("📜 Tus CDTs Constituidos Activos")
        df_mis_cdts = pd.DataFrame(u_data["cdt_list"])
        st.dataframe(df_mis_cdts, use_container_width=True)
        st.markdown("---")

    st.subheader("🏛️ Oferta de CDTs en 50 Entidades Bancarias de Colombia")
    
    cash_libre = float(u_data.get("cash", 500000.0))
    cols_banco = st.columns(3)

    for idx_b, item_b in enumerate(bancos_cdt_50):
        c_b = cols_banco[idx_b % 3]
        min_req = float(item_b['min_inversion'])
        
        with c_b:
            st.markdown(
                f"""
                <div class="trii-card-green">
                    <h3 style="margin:0; font-size: 1.1rem;">{item_b['logo']} {item_b['banco']}</h3>
                    <h2 style="color: #2ea043; margin: 4px 0;">{item_b['tasa_ea']}% E.A.</h2>
                    <p style="color: #cbd5e1; font-size: 0.82rem; margin:0;">🗓️ <b>Plazo:</b> {item_b['plazo_dias']} Días</p>
                    <p style="color: #cbd5e1; font-size: 0.82rem; margin:0;">💵 <b>Mínimo:</b> ${min_req:,.0f} COP</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander(f"📥 Abrir CDT en {item_b['banco']}"):
                if cash_libre >= min_req:
                    max_inversion_posible = int(cash_libre)
                    val_default = min(100000, max_inversion_posible)
                    if val_default < min_req:
                        val_default = int(min_req)

                    monto_apert = st.number_input(
                        f"Monto a invertir ({item_b['banco']}):",
                        min_value=int(min_req),
                        max_value=max_inversion_posible,
                        value=val_default,
                        step=10000,
                        key=f"monto_cdt_{idx_b}"
                    )
                    
                    renta_estimada = monto_apert * ((1 + item_b['tasa_ea']/100)**(item_b['plazo_dias']/365) - 1)
                    st.caption(f"💰 Rendimiento Neto Estimado: **+${renta_estimada:,.0f} COP**")

                    if st.button(f"Constituir CDT", key=f"btn_cdt_{idx_b}"):
                        u_data["cash"] -= monto_apert
                        nuevo_cdt = {
                            "banco": item_b['banco'],
                            "monto": monto_apert,
                            "tasa_ea": f"{item_b['tasa_ea']}%",
                            "plazo_dias": item_b['plazo_dias'],
                            "ganancia_estimada": f"${renta_estimada:,.0f} COP",
                            "fecha": datetime.datetime.now().strftime("%Y-%m-%d")
                        }
                        u_data.setdefault("cdt_list", []).append(nuevo_cdt)
                        save_user_to_db(usuario_activo, u_data)
                        st.success(f"¡CDT constituido con éxito en {item_b['banco']}!")
                        st.rerun()
                else:
                    st.warning(f"Necesitas mínimo ${min_req:,.0f} COP disponibles. Tu efectivo libre actual es de ${cash_libre:,.0f} COP.")

# ==========================================
# MÓDULO: RENTA FIJA Y BONOS TES
# ==========================================
elif menu == "Renta Fija y Bonos TES":
    st.title("📜 Renta Fija Sostenible y Bonos del Estado Colombiano (TES)")
    st.caption("Financiamiento de Infraestructura Pública y Deuda Soberana")

    st.markdown(
        """
        <div class="neon-card">
            <span class="concept-badge">Deuda Soberana de Colombia</span>
            <h3 style="margin-top: 5px;">🏛️ ¿Qué son los Bonos TES y la Renta Fija Pública?</h3>
            <p style="color: #cbd5e1; line-height: 1.7;">
                Los <b>Bonos TES (Títulos de Tesorería)</b> son la principal herramienta de deuda pública emitida por el Ministerio de Hacienda y Crédito Público de Colombia. 
                Al comprar un Bono TES, le estás prestando dinero directamente a la Nación Colombiana para financiar hospitales, colegios e infraestructura, a cambio de un cupón de interés fijo semestral o anual. Es considerado el activo con <b>el menor riesgo crediticio del país</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_bono1, col_bono2 = st.columns(2)

    with col_bono1:
        st.markdown(
            """
            <div class="trii-card-blue">
                <h3 style="color: #38bdf8;">🇨🇴 Bonos TES Clase B (Tasa Fija en Pesos)</h3>
                <p style="color: #cbd5e1;">Emisiones directas del Estado colombiano a plazos de 3, 5, 10 y 30 años.</p>
                <ul>
                    <li><b>Rendimiento Promedio:</b> 10.2% - 11.5% E.A.</li>
                    <li><b>Pagos:</b> Cupones Anuales Fijos.</li>
                    <li><b>Riesgo:</b> Soberano (Nación Colombiana).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

    with col_bono2:
        st.markdown(
            """
            <div class="trii-card-purple">
                <h3 style="color: #c084fc;">🏗️ Bonos Corporativos AAA (Ecopetrol / ISA)</h3>
                <p style="color: #cbd5e1;">Deuda emitida por grandes corporaciones industriales para ampliaciones de planta.</p>
                <ul>
                    <li><b>Rendimiento Promedio:</b> 11.8% - 12.8% E.A.</li>
                    <li><b>Pagos:</b> Cupones Semestrales.</li>
                    <li><b>Riesgo:</b> Corporativo con máxima calificación Crediticia AAA.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

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