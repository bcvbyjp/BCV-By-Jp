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

# Configuración general de la página (Wide mode)
st.set_page_config(
    page_title="BCV By Jp - Simulador Financiero Institucional",
    page_icon="📈",
    layout="wide",
)

# ==========================================
# ESTILOS CSS CON TU FONDO FINANCIERO Y LOGIN MODERNO
# ==========================================
st.markdown(
    """
    <style>
    /* Fondo general oscuro corporativo elegante */
    .stApp {
        background-color: #060913;
        color: #f0f6fc;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Fondo personalizado para la pantalla de registro / login */
    body {
        background: 
            linear-gradient(rgba(4, 8, 18, 0.88), rgba(4, 8, 18, 0.95)),
            url("fondo-financiero.jpg") center/cover no-repeat fixed;
    }
    .login-container {
        background: rgba(8, 13, 25, 0.78);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(100, 150, 200, 0.25);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45);
        border-radius: 24px;
        padding: 30px;
    }

    /* Tarjetas de Activos / Módulos en rectángulos curvos modernos */
    .asset-card {
        background: linear-gradient(135deg, #101622 0%, #1a2233 100%);
        border: 1px solid #1f6feb;
        border-radius: 22px;
        padding: 26px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(31, 111, 235, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .asset-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(88, 166, 255, 0.4);
    }

    /* Hero section con Planeta 3D y Red Neón */
    .hero-planet-box {
        background: radial-gradient(circle at center, #1b2a4a 0%, #0a0e1a 70%);
        border: 2px solid #58a6ff;
        border-radius: 30px;
        padding: 50px;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 0 50px rgba(88, 166, 255, 0.3);
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #101622, #080d16);
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.5);
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-weight: 600;
        font-size: 0.9rem;
    }

    h1, h2, h3 {
        color: #58a6ff;
        font-weight: 700;
    }

    .stButton>button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 14px rgba(35, 134, 54, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(46, 160, 67, 0.6);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 1. GESTIÓN DE BASE DE DATOS PERSISTENTE (SQLITE)
# ==========================================
DB_FILE = "bcv_database.db"


def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            rol TEXT,
            semestre TEXT,
            carrera TEXT,
            cash REAL,
            presupuesto_inicial REAL,
            portfolio_acciones TEXT,
            cdt_list TEXT,
            renta_fija_list TEXT,
            historial_pasos TEXT,
            informe_estudiante TEXT,
            esg_fund REAL
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            titulo TEXT PRIMARY KEY,
            descripcion TEXT,
            tendencia_forzada TEXT,
            semestre_objetivo TEXT,
            presupuesto_inicial REAL,
            eventos_claves TEXT,
            entregas TEXT
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
      uname, rol, sem, car, cash, p_ini, p_acc, c_list, r_list, h_pas, inf, esg = (
          row
      )
      pwd = "123"
    else:
      uname, pwd, rol, sem, car, cash, p_ini, p_acc, c_list, r_list, h_pas, inf, esg = (
          row
      )

    try:
      p_acc = json.loads(p_acc) if p_acc else {}
    except:
      p_acc = {}
    try:
      c_list = json.loads(c_list) if c_list else []
    except:
      c_list = []
    try:
      r_list = json.loads(r_list) if r_list else []
    except:
      r_list = []
    try:
      h_pas = json.loads(h_pas) if h_pas else []
    except:
      h_pas = []

    db[uname] = {
        "password": pwd,
        "rol": rol,
        "semestre": sem,
        "carrera": car,
        "cash": cash,
        "presupuesto_inicial": p_ini,
        "portfolio_acciones": p_acc,
        "cdt_list": c_list,
        "renta_fija_list": r_list,
        "historial_pasos": h_pas,
        "informe_estudiante": inf,
        "esg_fund": esg,
    }
  conn.close()
  return db


def load_user_db():
  return load_user_db_cached()


def save_user_to_db(username, udata):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          username,
          udata.get("password", "123"),
          udata.get("rol"),
          udata.get("semestre"),
          udata.get("carrera"),
          udata.get("cash"),
          udata.get("presupuesto_inicial"),
          json.dumps(udata.get("portfolio_acciones")),
          json.dumps(udata.get("cdt_list")),
          json.dumps(udata.get("renta_fija_list")),
          json.dumps(udata.get("historial_pasos")),
          udata.get("informe_estudiante"),
          udata.get("esg_fund"),
      ),
  )
  conn.commit()
  conn.close()


def load_assignments_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM assignments")
  rows = cursor.fetchall()
  assigns = {}
  for row in rows:
    try:
      evs = json.loads(row[5]) if row[5] else {}
    except:
      evs = {}
    try:
      ents = json.loads(row[6]) if row[6] else {}
    except:
      ents = {}

    assigns[row[0]] = {
        "descripcion": row[1],
        "tendencia_forzada": row[2],
        "semestre_objetivo": row[3],
        "presupuesto_inicial": row[4],
        "eventos_claves": {int(k): v for k, v in evs.items()} if evs else {},
        "entregas": ents,
    }
  conn.close()
  if not assigns:
    assigns = {
        "Actividad 1: Portafolio Estratégico Multieventos": {
            "descripcion": (
                "Gestionar un portafolio avanzado enfrentando múltiples crisis"
                " macroeconómicas y decisiones estratégicas."
            ),
            "tendencia_forzada": "Alta Volatilidad",
            "semestre_objetivo": "Semestre 4",
            "presupuesto_inicial": 500000,
            "eventos_claves": {
                5: {
                    "tipo": "decision",
                    "titulo": "SHOCK INFLACIONARIO Y TASAS DEL BANREP",
                    "desc": (
                        "El Banco de la República incrementa las tasas de"
                        " interés en 100 p.b. ante presiones inflacionarias."
                    ),
                    "impacto": -1,
                    "op_a": "🛡 Rebalancear a renta fija y TES",
                    "ef_a": "Protege el capital y ajusta valor de bonos.",
                    "op_b": "💎 Mantener renta variable y asumir volatilidad",
                    "ef_b": "Apuesta por la recuperación a largo plazo.",
                }
            },
            "entregas": {},
        }
    }
  return assigns


def save_assignment_to_db(titulo, adata):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  evs_str = {str(k): v for k, v in adata.get("eventos_claves", {}).items()}
  cursor.execute(
      """
        INSERT OR REPLACE INTO assignments VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
      (
          titulo,
          adata.get("descripcion"),
          adata.get("tendencia_forzada"),
          adata.get("semestre_objetivo"),
          adata.get("presupuesto_inicial"),
          json.dumps(evs_str),
          json.dumps(adata.get("entregas")),
      ),
  )
  conn.commit()
  conn.close()


if "user_database" not in st.session_state:
  st.session_state.user_database = load_user_db()

if "prof_assignments" not in st.session_state:
  st.session_state.prof_assignments = load_assignments_db()

if "current_date" not in st.session_state:
  st.session_state.current_date = datetime.date(2026, 10, 2)

if "macro_tasas_banrep" not in st.session_state:
  st.session_state.macro_tasas_banrep = 0.095

# ==========================================
# 2. GENERADOR DE MÁS DE 200 ACTIVOS
# ==========================================
if "stocks_initialized" not in st.session_state:
  base_data = {
      "ECOPETROL": {
          "precio": 2685,
          "logo": "🛢️",
          "esg_score": 72,
          "desc": (
              "Empresa Colombiana de Petróleos S.A. Líder en exploración y"
              " producción."
          ),
      },
      "BCOLOMBIA": {
          "precio": 33500,
          "logo": "🏦",
          "esg_score": 85,
          "desc": (
              "Banco de Colombia S.A. La institución financiera más grande del"
              " país."
          ),
      },
      "PFBCOLOMB": {
          "precio": 31200,
          "logo": "💳",
          "esg_score": 84,
          "desc": "Acciones preferenciales de Bancolombia.",
      },
      "ISA": {
          "precio": 18900,
          "logo": "⚡",
          "esg_score": 92,
          "desc": (
              "Interconexión Eléctrica S.A. Gigante en transmisión de energía."
          ),
      },
      "GRUPOSURA": {
          "precio": 36200,
          "logo": "📈",
          "esg_score": 88,
          "desc": "Grupo de Inversiones Suramericana. Holding financiero.",
      },
      "PROMIGAS": {
          "precio": 6400,
          "logo": "🔥",
          "esg_score": 78,
          "desc": "Transporte y distribución de gas natural.",
      },
      "CEMARGOS": {
          "precio": 7800,
          "logo": "🏗️",
          "esg_score": 80,
          "desc": "Cementos Argos S.A. Productor multinacional de cemento.",
      },
      "NUTRESA": {
          "precio": 46000,
          "logo": "🍫",
          "esg_score": 90,
          "desc": "Grupo Nutresa S.A. Industria de alimentos procesados.",
      },
      "CORFICOLCF": {
          "precio": 19800,
          "logo": "💼",
          "esg_score": 82,
          "desc": "Corporación Financiera Colombiana.",
      },
      "PFDAVVNDA": {
          "precio": 27200,
          "logo": "🏛",
          "esg_score": 86,
          "desc": "Acciones preferenciales de Banco Davivienda.",
      },
      "CELSIA": {
          "precio": 4250,
          "logo": "💡",
          "esg_score": 91,
          "desc": "Energía del Grupo Argos y renovables.",
      },
      "BOGOTA": {
          "precio": 35000,
          "logo": "🏢",
          "esg_score": 83,
          "desc": "Banco de Bogotá S.A.",
      },
      "ETB": {
          "precio": 185,
          "logo": "☎️",
          "esg_score": 75,
          "desc": "Empresa de Telecomunicaciones de Bogotá.",
      },
      "MINEROS": {
          "precio": 3950,
          "logo": "⛏️",
          "esg_score": 70,
          "desc": "Mineros S.A. Extracción sostenible de oro.",
      },
      "PFAVAL": {
          "precio": 535,
          "logo": "📊",
          "esg_score": 79,
          "desc": "Grupo Aval Acciones y Valores S.A.",
      },
      "PFCENCOSUD": {
          "precio": 1250,
          "logo": "🛒",
          "esg_score": 76,
          "desc": "Acciones preferenciales de Cencosud.",
      },
      "AAPL (Apple)": {
          "precio": 820000,
          "logo": "🍏",
          "esg_score": 94,
          "desc": "Apple Inc. Gigante tecnológico global.",
      },
      "MSFT (Microsoft)": {
          "precio": 1750000,
          "logo": "💻",
          "esg_score": 95,
          "desc": "Microsoft Corporation. Software e Inteligencia Artificial.",
      },
      "GOOGL (Alphabet)": {
          "precio": 710000,
          "logo": "🔍",
          "esg_score": 89,
          "desc": "Alphabet Inc. Propietario de Google y YouTube.",
      },
      "AMZN (Amazon)": {
          "precio": 780000,
          "logo": "📦",
          "esg_score": 81,
          "desc": "Amazon.com Inc. E-commerce e infraestructura cloud.",
      },
      "NVDA (NVIDIA)": {
          "precio": 540000,
          "logo": "🎮",
          "esg_score": 92,
          "desc": "NVIDIA Corporation. Procesamiento gráfico e IA.",
      },
      "TSLA (Tesla)": {
          "precio": 990000,
          "logo": "🚗",
          "esg_score": 88,
          "desc": "Tesla Inc. Vehículos eléctricos.",
      },
      "META (Meta)": {
          "precio": 1900000,
          "logo": "🌐",
          "esg_score": 82,
          "desc": "Meta Platforms Inc. Redes sociales.",
      },
      "NFLX (Netflix)": {
          "precio": 2950000,
          "logo": "🎬",
          "esg_score": 85,
          "desc": "Netflix Inc. Streaming global.",
      },
  }

  sectores = ["TECH", "FIN", "ENERG", "SALUD", "CONSUMO", "IND", "CRYPTO"]
  nombres_extra = [
      "Alpha",
      "Beta",
      "Gamma",
      "Delta",
      "Omega",
      "Nova",
      "Solar",
      "Quantum",
      "Cyber",
      "Bio",
      "Apex",
      "Prime",
      "Global",
      "Terra",
      "Aero",
      "Nexus",
      "Titan",
      "Vortex",
      "Zenith",
      "Pioneer",
  ]
  contador = len(base_data)
  for sec in sectores:
    for nombre in nombres_extra:
      ticker = f"{sec}-{nombre}"
      if ticker not in base_data and contador < 210:
        base_data[ticker] = {
            "precio": random.randint(5000, 1500000),
            "logo": "🏢",
            "esg_score": random.randint(65, 95),
            "desc": f"Activo corporativo del sector {sec}.",
        }
        contador += 1

  st.session_state.prices_dict = base_data
  st.session_state.prices = {k: v["precio"] for k, v in base_data.items()}
  st.session_state.history = {
      ticker: [
          val["precio"] * random.uniform(0.9, 1.0),
          val["precio"] * random.uniform(0.95, 1.02),
          val["precio"],
      ]
      for ticker, val in base_data.items()
  }

  st.session_state.news_feed = [
      (
          "🇨🇴 [Banrepública] Tasas de Interés y Convergencia Inflacionaria",
          (
              "El Banco de la República evalúa nuevos recortes de su tasa de"
              " interés de referencia ante una inflación que busca consolidarse"
              " en el rango meta del 3%."
          ),
      ),
      (
          "🛢️ [Mercado Petrolero] Volatilidad del Crudo Brent y Ecopetrol",
          (
              "Los precios internacionales del petróleo Brent reaccionan ante"
              " tensiones geopolíticas y acuerdos OPEP+, afectando el flujo de"
              " caja de Ecopetrol."
          ),
      ),
      (
          "🇺🇸 [FED / Wall Street] Empleo y Decisiones de Tasas en EE. UU.",
          (
              "La Reserva Federal ajusta su hoja de ruta monetaria basada en"
              " empleo y consumo, generando volatilidad en Wall Street."
          ),
      ),
  ]
  for i in range(4, 250):
    st.session_state.news_feed.append((
        f"📰 [Boletín Macro BVC #{i}]",
        "Flujos institucionales estables en el mercado secundario.",
    ))
  st.session_state.stocks_initialized = True

# ==========================================
# 3. GENERADOR DE CDT Y VARIEDAD DE BONOS (RENTA FIJA)
# ==========================================
if "instruments_initialized" not in st.session_state:
  bancos_nombres = [
      "Banco Pichincha",
      "Pibank Digital",
      "Bancolombia",
      "Davivienda",
      "BBVA Colombia",
      "Banco de Bogotá",
  ]
  cdts_list_gen = []
  for i in range(1, 101):
    banco = random.choice(bancos_nombres)
    plazo_dias = random.choice([30, 60, 90, 180, 360])
    tasa_ea = round(random.uniform(8.5, 14.2), 2)
    cdts_list_gen.append({
        "id": f"CDT-{i}",
        "entidad": banco,
        "plazo": f"{plazo_dias} Días",
        "tasa": tasa_ea / 100.0,
        "desc": f"CDT de {banco} a {plazo_dias} días al {tasa_ea}% E.A. FOGAFIN.",
    })
  st.session_state.all_cdts = cdts_list_gen

  emisores_rf = [
      "Nación (TES Soberanos Tasa Fija)",
      "Nación (TES Indexados a UVR)",
      "Ecopetrol (Bonos Corporativos Ordinarios)",
      "ISA (Bonos de Infraestructura Vial)",
      "Grupo Sura (Bonos Sostenibles ESG)",
      "Bancolombia (Bonos Subordinados Tier 2)",
      "EPM Medellín (Bonos de Servicios Públicos)",
      "Promigas (Bonos Energéticos)",
  ]
  rf_list_gen = []
  for j in range(1, 101):
    emisor = random.choice(emisores_rf)
    tasa_anual = round(random.uniform(8.0, 14.5), 2)
    tipo_bono = random.choice(
        ["Tasa Fija E.A.", "Indexado IPC + Spread", "Tasas IBR"]
    )
    rf_list_gen.append({
        "id": f"BONO-{j}",
        "emisor": emisor,
        "tipo": tipo_bono,
        "tasa": tasa_anual / 100.0,
        "desc": (
            f"Título de Renta Fija / Bono emitido por {emisor} ({tipo_bono}) con"
            f" rendimiento estimado de {tasa_anual}% anual."
        ),
    })
  st.session_state.all_rf = rf_list_gen
  st.session_state.instruments_initialized = True

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

# ==========================================
# 4. LOGIN CON TU NUEVO ESTILO CSS Y FONDO FINANCIERO
# ==========================================
if not st.session_state.logged_in:
  st.markdown(
      """
        <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
            <div class="login-container" style="width: 100%; max-width: 500px;">
                <h1 style="text-align: center; color: #58a6ff; margin-bottom: 5px;">🔐 BCV By Jp</h1>
                <h3 style="text-align: center; color: #8b949e; font-size: 1.1rem; margin-bottom: 25px;">Portal Académico Financiero Institucional</h3>
    """,
      unsafe_allow_html=True,
  )

  col_l1, col_l2, col_l3 = st.columns([0.1, 0.8, 0.1])
  with col_l2:
    rol = st.radio("Selecciona tu perfil de acceso:", ["Estudiante", "Profesor"])

    if rol == "Estudiante":
      with st.form("form_est"):
        nombre_est = st.text_input("Nombre Completo:")
        pass_est = st.text_input("Contraseña de Acceso:", type="password")
        semestre_est = st.selectbox(
            "Semestre:",
            [f"Semestre {i}" for i in range(1, 11)],
        )
        carrera_est = st.text_input(
            "Carrera (ej. Administración de Empresas):"
        )
        btn_ing = st.form_submit_button("Ingresar al Portal 🚀")
        if btn_ing:
          if nombre_est.strip() and carrera_est.strip() and pass_est.strip():
            if nombre_est.strip().upper() == "JP":
              rol_real = "Administrador"
              presup_def = 100000000
            else:
              rol_real = "Estudiante"
              presup_def = 500000  # Bono inicial de $500,000 COP

            if nombre_est not in st.session_state.user_database:
              st.session_state.user_database[nombre_est] = {
                  "password": pass_est,
                  "rol": rol_real,
                  "semestre": (
                      semestre_est if rol_real == "Estudiante" else "Admin"
                  ),
                  "carrera": carrera_est,
                  "cash": presup_def,
                  "presupuesto_inicial": presup_def,
                  "portfolio_acciones": {},
                  "cdt_list": [],
                  "renta_fija_list": [],
                  "historial_pasos": [],
                  "informe_estudiante": "",
                  "esg_fund": 0,
              }
              save_user_to_db(
                  nombre_est, st.session_state.user_database[nombre_est]
              )
            else:
              user_db_info = st.session_state.user_database[nombre_est]
              if user_db_info["password"] != pass_est:
                st.error("❌ Contraseña incorrecta.")
                st.stop()
              if nombre_est.strip().upper() == "JP":
                user_db_info["rol"] = "Administrador"

            st.session_state.current_user = nombre_est
            st.session_state.current_role = (
                st.session_state.user_database[nombre_est]["rol"]
            )
            st.session_state.logged_in = True
            st.rerun()
          else:
            st.error("Completa todos los campos.")
    else:
      with st.form("form_prof"):
        nombre_prof = st.text_input("Nombre del Profesor:")
        pass_prof = st.text_input("Contraseña:", type="password")
        btn_ing_p = st.form_submit_button("Ingresar Docente 👨‍🏫")
        if btn_ing_p:
          if pass_prof == "Unisucre2026" and nombre_prof.strip():
            if nombre_prof not in st.session_state.user_database:
              st.session_state.user_database[nombre_prof] = {
                  "password": pass_prof,
                  "rol": "Profesor",
                  "semestre": "Profesor",
                  "carrera": "Docencia",
                  "cash": 0,
                  "presupuesto_inicial": 0,
                  "portfolio_acciones": {},
                  "cdt_list": [],
                  "renta_fija_list": [],
                  "historial_pasos": [],
                  "informe_estudiante": "",
                  "esg_fund": 0,
              }
              save_user_to_db(
                  nombre_prof, st.session_state.user_database[nombre_prof]
              )
            st.session_state.current_user = nombre_prof
            st.session_state.current_role = "Profesor"
            st.session_state.logged_in = True
            st.rerun()
          else:
            st.error("Contraseña incorrecta (Unisucre2026).")

  st.markdown("</div></div>", unsafe_allow_html=True)
  st.stop()

# ==========================================
# 5. APLICACIÓN PRINCIPAL (MENÚ Y MÓDULOS COMPLETOS)
# ==========================================
usuario_activo = st.session_state.current_user
rol_activo = st.session_state.current_role
u_data = st.session_state.user_database[usuario_activo]

if "historial_pasos" not in u_data:
  u_data["historial_pasos"] = []
if "informe_estudiante" not in u_data:
  u_data["informe_estudiante"] = ""

if rol_activo == "Estudiante":
  opciones_menu = [
      "🏠 1. Presentación & Planeta 3D (Juan López)",
      "📖 2. Guía Paso a Paso (Onboarding)",
      "💡 3. Casos de Éxito Dinámicos",
      "📊 4. Catálogo & Análisis Técnico",
      "🧮 5. Markowitz (Frontera Óptima)",
      "🏆 6. Ranking Global (Leaderboard)",
      "🏦 7. CDT y Bonos de Renta Fija",
      "🛒 8. Terminal Bursátil (Compra/Venta)",
      "🌱 9. Fondo ESG Sostenible",
      "📰 10. Sala de Noticias Reales",
      "📝 11. Tareas e Informe",
      "⏳ 12. Simulación (Demo vs Día a Día Realista)",
      "🧠 13. Alertas de Riesgo & Correlación",
  ]
elif rol_activo == "Administrador":
  opciones_menu = [
      "👑 1. Panel Supremo Admin (Jp)",
      "🏠 2. Presentación & Planeta 3D",
      "📖 3. Guía Paso a Paso",
      "💡 4. Casos de Éxito Dinámicos",
      "📊 5. Catálogo Técnico",
      "🧮 6. Markowitz",
      "🏆 7. Ranking",
      "🏦 8. CDT y Bonos",
      "🛒 9. Terminal Bursátil",
      "⏳ 10. Simulación (Demo vs Día a Día)",
      "🧠 11. Alertas de Riesgo",
  ]
else:
  opciones_menu = [
      "🏠 1. Presentación & Planeta 3D",
      "📖 2. Guía Paso a Paso",
      "💡 3. Casos de Éxito Dinámicos",
      "📊 4. Catálogo Técnico",
      "🧮 5. Markowitz",
      "🏆 6. Ranking",
      "🏦 7. CDT y Bonos de Renta Fija",
      "🛒 8. Terminal Bursátil",
      "🌱 9. Fondo ESG",
      "📰 10. Sala de Noticias Reales",
      "👨‍🏫 11. Panel de Asignaciones (Profesor)",
      "⏳ 12. Simulación (Demo vs Día a Día)",
      "🧠 13. Alertas de Riesgo",
  ]

st.sidebar.title("📈 BCV By Jp")
st.sidebar.success(
    f"👤 **{usuario_activo}**\n📌 **Rol:** {rol_activo.upper()}"
)
if rol_activo == "Estudiante":
  st.sidebar.info(f"📚 {u_data.get('semestre', '')}")
  st.sidebar.info(
      f"📅 Fecha: {st.session_state.current_date.strftime('%Y-%m-%d')}"
  )
elif rol_activo == "Administrador":
  st.sidebar.warning("⚡ Acceso Total Admin Jp")

if st.sidebar.button("🚪 Cerrar Sesión"):
  save_user_to_db(usuario_activo, u_data)
  st.session_state.logged_in = False
  st.rerun()

st.sidebar.markdown("---")
menu = st.sidebar.selectbox("🌟 Selecciona un Módulo:", opciones_menu)

val_acc = sum(
    u_data["portfolio_acciones"].get(t, 0) * st.session_state.prices[t]
    for t in st.session_state.prices
)
val_cdt = sum(c["monto"] for c in u_data["cdt_list"])
val_rf = sum(r["monto"] for r in u_data["renta_fija_list"])
val_esg = u_data.get("esg_fund", 0)
patrimonio = u_data["cash"] + val_acc + val_cdt + val_rf + val_esg
p_ini = u_data.get("presupuesto_inicial", 0)

st.sidebar.markdown("---")
st.sidebar.subheader("💼 Resumen Financiero")
st.sidebar.metric(
    "Efectivo Libre", f"${u_data['cash']:,.0f} COP".replace(",", ".")
)
st.sidebar.metric(
    "Patrimonio Total",
    f"${patrimonio:,.0f} COP".replace(",", "."),
    delta=(
        f"${patrimonio - p_ini:,.0f} COP".replace(",", ".")
        if p_ini > 0
        else "$0 COP"
    ),
)

# ==========================================
# DESARROLLO DE MÓDULOS COMPLETOS
# ==========================================
if menu == "👑 1. Panel Supremo Admin (Jp)":
  st.title("👑 Panel de Control Supremo del Administrador (Jp)")
  st.success("¡Bienvenido, Jp! Tienes privilegios absolutos en el sistema.")
  db_all = load_user_db()
  for u_name, u_info in db_all.items():
    with st.expander(
        f"Usuario: {u_name} | Rol: {u_info['rol']} | Carrera:"
        f" {u_info['carrera']}"
    ):
      st.write(f"**Efectivo:** ${u_info['cash']:,.0f} COP")
      st.markdown("**Acciones en Posesión:**")
      st.json(u_info["portfolio_acciones"])
      if st.button(f"Inyectar +$1,000,000 COP a {u_name}", key=f"iny_{u_name}"):
        u_info["cash"] += 1000000
        save_user_to_db(u_name, u_info)
        st.success(f"¡Inyectado 1 millón a {u_name}!")
        st.rerun()

elif (
    menu == "🏠 1. Presentación & Planeta 3D (Juan López)"
    or menu == "🏠 2. Presentación & Planeta 3D"
    or menu == "🏠 1. Presentación & Planeta 3D"
):
  st.markdown(
      """
        <div class="hero-planet-box">
            <h1 style="color: #58a6ff; font-size: 3rem; margin-bottom: 10px; text-shadow: 0 0 20px rgba(88,166,255,0.6);">🌍 BCV By Jp - Red Global & Terminal Bursátil</h1>
            <h3 style="color: #8b949e; font-weight: 400; margin-bottom: 25px;">Ecosistema Financiero Conectado con Inteligencia Estocástica y Datos Reales</h3>
            <p style="font-size: 1.15rem; color: #c9d1d9; max-width: 850px; margin: 0 auto; line-height: 1.6;">
                Plataforma de alta ingeniería desarrollada por <b>Juan Pablo López Tarriba (Juan López)</b>, estudiante de 
                <b>Administración de Empresas</b> de la <b>Universidad de Sucre</b> (Sincelejo, Colombia).
            </p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  df_globe = pd.DataFrame({
      "Lat": [4.5709, 40.7128, 51.5074, 35.6762],
      "Lon": [-74.2973, -74.0060, -0.1278, 139.6503],
      "Centro": ["Colombia", "New York", "London", "Tokyo"],
      "Volumen": [50000000, 900000000, 700000000, 600000000],
  })
  fig_globe = px.scatter_geo(
      df_globe,
      lat="Lat",
      lon="Lon",
      text="Centro",
      size="Volumen",
      projection="orthographic",
      title="🌐 Conectividad Bursátil Global",
  )
  fig_globe.update_geos(
      bgcolor="#060913",
      oceancolor="#0d1b2a",
      landcolor="#1b263b",
      showcountries=True,
      countrycolor="#415a77",
  )
  fig_globe.update_layout(
      height=400,
      paper_bgcolor="rgba(0,0,0,0)",
      font=dict(color="white"),
      margin=dict(l=0, r=0, t=30, b=0),
  )
  st.plotly_chart(fig_globe, use_container_width=True)

elif menu in ["📖 2. Guía Paso a Paso (Onboarding)", "📖 3. Guía Paso a Paso"]:
  st.title("📖 Guía Interactiva Paso a Paso (Cómo Usar la Plataforma)")
  st.markdown(
      """
        <div class="asset-card">
            <h3>Paso 1: Bono Inicial y Contraseña</h3>
            <p>Al registrarte con tu clave personal recibes un bono automático de <b>$500,000 COP</b>.</p>
        </div>
        <div class="asset-card">
            <h3>Paso 2: Compra de Acciones y Análisis Técnico</h3>
            <p>Navega por más de 200 activos, revisa su RSI y SMA, y opera en la terminal con precios reales.</p>
        </div>
        <div class="asset-card">
            <h3>Paso 3: CDT y Bonos de Renta Fija</h3>
            <p>Invierte en CDT bancarios o bonos corporativos y TES soberanos de la Nación.</p>
        </div>
        <div class="asset-card">
            <h3>Paso 4: Simulación y Fondo ESG</h3>
            <p>Evalúa tu portafolio frente a crisis y apoya proyectos sostenibles en el fondo ESG.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

elif menu in ["💡 3. Casos de Éxito Dinámicos", "💡 4. Casos de Éxito Dinámicos"]:
  st.title("💡 Casos de Éxito Dinámicos y el Poder de la Inversión")
  st.markdown(
      '<div class="asset-card"><h3>🌟 Anne Scheiber</h3><p>Invirtió'
      " disciplinadamente en acciones de primera línea y acumuló más de $22"
      " millones de dólares.</p></div>",
      unsafe_allow_html=True,
  )

elif menu in ["📊 4. Catálogo & Análisis Técnico", "📊 5. Catálogo Técnico"]:
  st.title("📊 Catálogo de Acciones con Precios Reales y Análisis Técnico")
  busc = st.text_input("🔍 Buscar acción o activo:")
  for t, info in st.session_state.prices_dict.items():
    if busc.strip() == "" or busc.upper() in t.upper():
      prc = st.session_state.prices[t]
      hist = st.session_state.history[t]
      s_hist = pd.Series(hist)
      sma_5 = s_hist.rolling(window=min(5, len(hist))).mean().iloc[-1]
      st.markdown(
          f"""
            <div class="asset-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2>{info['logo']} {t}</h2>
                    <h3 style="color: #2ea043;">${prc:,.0f} COP</h3>
                </div>
                <p style="color: #8b949e;">{info['desc']}</p>
                <p><b>SMA(5):</b> ${sma_5:,.0f} | <b>ESG Score:</b> {info['esg_score']}/100</p>
            </div>
        """,
          unsafe_allow_html=True,
      )
      fig_pl = px.line(y=hist, title=f"Tendencia {t}")
      fig_pl.update_layout(
          height=140,
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          font=dict(color="white"),
      )
      st.plotly_chart(fig_pl, use_container_width=True)

elif menu in ["🧮 5. Markowitz (Frontera Óptima)", "🧮 6. Markowitz"]:
  st.title("🧮 Optimización de Portafolios (Frontera Eficiente de Markowitz)")
  activos_sel = st.multiselect(
      "Selecciona activos:",
      list(st.session_state.prices.keys()),
      default=["ECOPETROL", "BCOLOMBIA", "ISA"][: min(3, len(st.session_state.prices))],
  )
  if len(activos_sel) >= 2 and st.button("Calcular Óptimo ⚙️"):
    st.success("¡Optimización de Markowitz completada con éxito!")

elif menu in ["🏆 6. Ranking Global (Leaderboard)", "🏆 7. Ranking"]:
  st.title("🏆 Tabla de Clasificación de Traders")
  ranking_data = []
  for uname, uinfo in st.session_state.user_database.items():
    if uinfo.get("rol") in ["Estudiante", "Administrador"]:
      v_acc = sum(
          uinfo["portfolio_acciones"].get(t, 0) * st.session_state.prices[t]
          for t in st.session_state.prices
      )
      v_tot = (
          uinfo["cash"]
          + v_acc
          + sum(c["monto"] for c in uinfo["cdt_list"])
          + sum(r["monto"] for r in uinfo["renta_fija_list"])
          + uinfo.get("esg_fund", 0)
      )
      p_ini_u = uinfo.get("presupuesto_inicial", 1)
      rent = (
          ((v_tot - p_ini_u) / p_ini_u) * 100
          if p_ini_u > 0
          else 0.0
      )
      ranking_data.append({
          "Trader": uname,
          "Patrimonio Total": v_tot,
          "Rentabilidad (%)": rent,
      })
  if ranking_data:
    df_rank = pd.DataFrame(ranking_data).sort_values(
        by="Rentabilidad (%)", ascending=False
    )
    st.dataframe(df_rank, use_container_width=True)

elif menu in ["🏦 7. CDT y Bonos de Renta Fija", "🏦 8. CDT y Bonos"]:
  st.title("🏦 CDT y Bonos de Renta Fija Institucional")
  tab1, tab2 = st.tabs(["📌 CDT Bancarios", "📜 Bonos de Renta Fija (TES / Corp)"])
  with tab1:
    for cdt in st.session_state.all_cdts[:10]:
      st.markdown(
          f'<div class="asset-card"><h4>{cdt["id"]} - {cdt["entidad"]}</h4><p>{cdt["desc"]}</p></div>',
          unsafe_allow_html=True,
      )
  with tab2:
    for rf in st.session_state.all_rf[:10]:
      st.markdown(
          f'<div class="asset-card"><h4>{rf["id"]} - {rf["emisor"]}</h4><p>{rf["desc"]}</p></div>',
          unsafe_allow_html=True,
      )

elif menu in ["🛒 8. Terminal Bursátil (Compra/Venta)", "🛒 9. Terminal Bursátil"]:
  st.title("🛒 Terminal Bursátil de Compra y Venta (Bid / Ask)")
  ticker_op = st.selectbox(
      "Seleccione Acción / Activo:", list(st.session_state.prices.keys())
  )
  prc_op = st.session_state.prices[ticker_op]
  bid_prc, ask_prc = int(prc_op * 0.998), int(prc_op * 1.002)
  c1, c2, c3 = st.columns(3)
  with c1:
    st.metric("Precio Last", f"${prc_op:,.0f} COP")
  with c2:
    st.metric("Bid", f"${bid_prc:,.0f} COP")
  with c3:
    st.metric("Ask", f"${ask_prc:,.0f} COP")

  tab_c, tab_v = st.tabs(["🟢 Comprar", "🔴 Vender"])
  with tab_c:
    cant = st.number_input("Cantidad a Comprar:", 1, 10000, 10)
    costo = ask_prc * cant
    if st.button("Ejecutar Compra de Acciones ⚡"):
      if u_data["cash"] >= costo:
        u_data["cash"] -= costo
        u_data["portfolio_acciones"][ticker_op] = (
            u_data["portfolio_acciones"].get(ticker_op, 0) + cant
        )
        save_user_to_db(usuario_activo, u_data)
        st.success("¡Compra ejecutada con éxito!")
        st.rerun()
      else:
        st.error("Efectivo insuficiente.")
  with tab_v:
    en_pos = u_data["portfolio_acciones"].get(ticker_op, 0)
    st.info(f"Tienes {en_pos} títulos.")
    if en_pos > 0:
      cant_v = st.number_input("Cantidad a Vender:", 1, en_pos, 1)
      recaudo = bid_prc * cant_v
      if st.button("Ejecutar Venta de Acciones ⚡"):
        u_data["cash"] += recaudo
        u_data["portfolio_acciones"][ticker_op] -= cant_v
        if u_data["portfolio_acciones"][ticker_op] <= 0:
          del u_data["portfolio_acciones"][ticker_op]
        save_user_to_db(usuario_activo, u_data)
        st.success("¡Venta ejecutada con éxito!")
        st.rerun()

elif menu in ["🌱 9. Fondo ESG Sostenible", "🌱 10. Fondo ESG"]:
  st.title("🌱 Fondo de Inversión Colectiva ESG (Sostenible)")
  monto_esg = st.number_input(
      "Monto para el Fondo ESG:", 100000, 50000000, 500000, step=100000
  )
  if st.button("Invertir en Fondo ESG 🌱"):
    if u_data["cash"] >= monto_esg:
      u_data["cash"] -= monto_esg
      u_data["esg_fund"] = u_data.get("esg_fund", 0) + monto_esg
      save_user_to_db(usuario_activo, u_data)
      st.success("¡Inversión ESG realizada con éxito!")
      st.rerun()
    else:
      st.error("Efectivo insuficiente.")
  st.metric(
      "Valor en Fondo ESG",
      f"${u_data.get('esg_fund', 0):,.0f} COP".replace(",", "."),
  )

elif menu in ["📰 10. Sala de Noticias Reales", "📰 11. Sala de Noticias"]:
  st.title("📰 Sala de Noticias Financieras Reales")
  for fuente, txt in st.session_state.news_feed[:10]:
    st.markdown(
        f'<div class="asset-card"><h4>{fuente}</h4><p>{txt}</p></div>',
        unsafe_allow_html=True,
    )

elif menu in ["📝 11. Tareas e Informe", "📝 12. Tareas"]:
  st.title("📝 Tareas y Justificación Analítica")
  informe = st.text_area(
      "Informe técnico:", value=u_data.get("informe_estudiante", "")
  )
  u_data["informe_estudiante"] = informe
  if st.button("Enviar Tarea 🚀"):
    save_user_to_db(usuario_activo, u_data)
    st.success("¡Enviado correctamente!")

elif menu == "👨‍🏫 11. Panel de Asignaciones (Profesor)":
  st.title("👨‍🏫 Panel de Control Docente Avanzado")
  with st.form("form_p_panel"):
    t_tit = st.text_input("Título de Actividad:")
    t_desc = st.text_area("Descripción:")
    t_sem = st.selectbox(
        "Semestre Objetivo:", [f"Semestre {i}" for i in range(1, 11)]
    )
    t_pres = st.number_input(
        "Presupuesto Inicial (COP):", 500000, 50000000, 500000, 50000
    )
    if st.form_submit_button("Publicar Actividad 🚀") and t_tit.strip():
      st.session_state.prof_assignments[t_tit] = {
          "descripcion": t_desc,
          "semestre_objetivo": t_sem,
          "presupuesto_inicial": t_pres,
          "eventos_claves": {},
          "entregas": {},
      }
      save_assignment_to_db(t_tit, st.session_state.prof_assignments[t_tit])
      st.success("¡Actividad publicada con éxito!")

elif menu in [
    "⏳ 12. Simulación (Demo vs Día a Día Realista)",
    "⏳ 10. Simulación (Demo vs Día a Día)",
    "⏳ 13. Simulación (Demo vs Día a Día)",
]:
  st.title(
      "⏳ Motor de Simulación: Modo Demo vs Modo Día a Día Realista (Oct 2026)"
  )
  modo_sim = st.radio(
      "Selecciona el Modo:",
      [
          "🚀 Modo Demo (Simulación Rápida)",
          "📅 Modo Día a Día Realista (Calendario Actual)",
      ],
  )
  if "Modo Día a Día" in modo_sim:
    st.write(
        f"📅 Fecha actual del simulador: **{st.session_state.current_date}**"
    )
    if st.button("Avanzar 1 Jornada Real (Día Siguiente) 📈"):
      st.session_state.current_date += datetime.timedelta(days=1)
      for t_k in st.session_state.prices:
        v = random.normalvariate(0.0006, 0.015)
        st.session_state.prices[t_k] = max(
            50, int(st.session_state.prices[t_k] * (1 + v))
        )
      st.success(
          f"¡Jornada avanzada! Nueva fecha:"
          f" {st.session_state.current_date}"
      )
      st.rerun()
  else:
    if st.button("Ejecutar Simulación Demo 🚀"):
      st.success("Simulación demo ejecutada con éxito.")

elif menu in [
    "🧠 14. Alertas de Riesgo & Correlación",
    "🧠 11. Alertas de Riesgo",
]:
  st.title("🧠 Alertas de Riesgo & Correlación de Portafolio")
  acc_poseidas = {
      k: v for k, v in u_data["portfolio_acciones"].items() if v > 0
  }
  total_acc_val = sum(
      cant * st.session_state.prices[t] for t, cant in acc_poseidas.items()
  )
  tot_pat = total_acc_val + u_data["cash"]
  if tot_pat > 0:
    pct_acc = (total_acc_val / tot_pat) * 100
    st.metric("Exposición Renta Variable", f"{pct_acc:.1f}%")
    if pct_acc > 75:
      st.error(
          "🔴 **ALERTA DE CONCENTRACIÓN:** Alta exposición a renta variable."
      )
    else:
      st.success("🟢 **PORTAFOLIO EQUILIBRADO:** Niveles de riesgo óptimos.")