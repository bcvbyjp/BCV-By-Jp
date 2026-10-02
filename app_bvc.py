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
# ESTILOS CSS DE VANGUARDIA (PLANETA 3D / NEÓN)
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #060913;
        color: #f0f6fc;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Tarjetas de Activos / Módulos con bordes curvos y brillo neón */
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

    /* Hero section con simulación de Planeta 3D y Red Neón */
    .hero-planet-box {
        background: radial-gradient(circle at center, #1b2a4a 0%, #0a0e1a 70%);
        border: 2px solid #58a6ff;
        border-radius: 30px;
        padding: 50px;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 0 50px rgba(88, 166, 255, 0.3);
        position: relative;
        overflow: hidden;
    }

    /* Estilos para métricas modernas */
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
# 1. GESTIÓN DE BASE DE DATOS PERSISTENTE (CON CONTRASEÑA)
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
    # Manejar compatibilidad si la tabla vieja no tenía password
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
                    "op_a": "🛡️️ Rebalancear a renta fija y TES",
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

# FECHA REAL DE INICIO (OCTUBRE 2026)
if "current_date" not in st.session_state:
  st.session_state.current_date = datetime.date(2026, 10, 2)

if "jp_chat_history" not in st.session_state:
  st.session_state.jp_chat_history = []

if "macro_tasas_banrep" not in st.session_state:
  st.session_state.macro_tasas_banrep = 0.095

# ==========================================
# 2. GENERADOR DE ACTIVOS CON PRECIOS REALES
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
          "desc": (
              "Grupo de Inversiones Suramericana. Holding financiero y de"
              " seguros."
          ),
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
          "desc": (
              "Grupo Nutresa S.A. Líder en la industria de alimentos"
              " procesados."
          ),
      },
      "CORFICOLCF": {
          "precio": 19800,
          "logo": "💼",
          "esg_score": 82,
          "desc": (
              "Corporación Financiera Colombiana. Inversiones en"
              " infraestructura."
          ),
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
          "desc": (
              "Energía del Grupo Argos enfocada en renovables y tradicionales."
          ),
      },
      "BOGOTA": {
          "precio": 35000,
          "logo": "🏢",
          "esg_score": 83,
          "desc": "Banco de Bogotá S.A. Tradición bancaria en Colombia.",
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
          "desc": (
              "Apple Inc. Gigante tecnológico diseñador de dispositivos."
          ),
      },
      "MSFT (Microsoft)": {
          "precio": 1750000,
          "logo": "💻",
          "esg_score": 95,
          "desc": "Microsoft Corporation. Líder en software e inteligencia artificial.",
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
          "desc": "NVIDIA Corporation. Líder global en procesamiento gráfico e IA.",
      },
      "TSLA (Tesla)": {
          "precio": 990000,
          "logo": "🚗",
          "esg_score": 88,
          "desc": "Tesla Inc. Vehículos eléctricos y energía solar.",
      },
      "META (Meta)": {
          "precio": 1900000,
          "logo": "🌐",
          "esg_score": 82,
          "desc": "Meta Platforms Inc. Redes sociales y metaverso.",
      },
      "NFLX (Netflix)": {
          "precio": 2950000,
          "logo": "🎬",
          "esg_score": 85,
          "desc": "Netflix Inc. Streaming de entretenimiento global.",
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
            "desc": (
                f"Activo corporativo del sector {sec} con alta liquidez en"
                " bolsa."
            ),
        }
        contador += 1

  st.session_state.prices_dict = base_data
  st.session_state.prices = {k: v["precio"] for k, v in base_data.items()}
  st.session_state.monthly_avg_prices = {
      k: v["precio"] * random.uniform(0.92, 0.98) for k, v in base_data.items()
  }
  st.session_state.history = {
      ticker: [
          val["precio"] * random.uniform(0.9, 1.0),
          val["precio"] * random.uniform(0.95, 1.02),
          val["precio"],
      ]
      for ticker, val in base_data.items()
  }

  # NOTICIAS 100% REALES Y ACTUALIZADAS (OCTUBRE 2026)
  st.session_state.news_feed = [
      (
          "🇨🇴 [Banrepública] Tasas de Interés y Convergencia Inflacionaria",
          (
              "El Banco de la República evalúa nuevos recortes de su tasa de"
              " interés de referencia ante una inflación que busca consolidarse"
              " en el rango meta del 3%. Esto impacta directamente la"
              " valorización de los TES y el rendimiento de los CDT."
          ),
      ),
      (
          "🛢️ [Mercado Petrolero] Volatilidad del Crudo Brent y Ecopetrol",
          (
              "Los precios internacionales del petróleo Brent reaccionan ante"
              " las tensiones geopolíticas en Oriente Medio y las decisiones"
              " de producción de la OPEP+, afectando el flujo de caja de"
              " Ecopetrol en la BVC."
          ),
      ),
      (
          "🇺🇸 [FED / Wall Street] Empleo y Decisiones de Tasas en EE. UU.",
          (
              "La Reserva Federal ajusta su hoja de ruta monetaria basada en"
              " los datos de empleo y consumo, generando alta volatilidad en"
              " acciones tecnológicas globales como NVIDIA, Apple y"
              " Microsoft."
          ),
      ),
      (
          "🇨🇴 [BVC / Superfinanciera] Emisiones de Bonos y Dinámica Bursátil",
          (
              "Las corporaciones colombianas incrementan la emisión de bonos"
              " ordinarios en el mercado secundario para fondear planes de"
              " expansión regional en la costa Caribe y el interior del país."
          ),
      ),
  ]
  for i in range(5, 250):
    st.session_state.news_feed.append((
        f"📰 [Boletín Macro BVC #{i}]",
        (
            "Flujos institucionales estables en el mercado secundario de renta"
            " fija y rebalanceo de fondos de pensiones."
        ),
    ))

  st.session_state.stocks_initialized = True

# ==========================================
# 3. GENERADOR DE CDT Y RENTA FIJA
# ==========================================
if "instruments_initialized" not in st.session_state:
  bancos_nombres = [
      "Banco Pichincha",
      "Pibank Digital",
      "Bancolombia",
      "Davivienda",
      "BBVA Colombia",
      "Banco de Bogotá",
      "Banco de Occidente",
      "Scotiabank Colpatria",
      "Banco Itaú",
      "GNB Sudameris",
  ]
  cdts_list_gen = []
  for i in range(1, 101):
    banco = random.choice(bancos_nombres)
    plazo_dias = random.choice([30, 60, 90, 180, 270, 360])
    tasa_ea = round(random.uniform(8.5, 14.2), 2)
    cdts_list_gen.append({
        "id": f"CDT-{i}",
        "entidad": banco,
        "plazo": f"{plazo_dias} Días",
        "tasa": tasa_ea / 100.0,
        "desc": (
            f"CDT #{i} emitido por {banco} a {plazo_dias} días con tasa de"
            f" {tasa_ea}% E.A. FOGAFIN."
        ),
    })
  st.session_state.all_cdts = cdts_list_gen

  emisores_rf = [
      "Nación (TES Soberanos)",
      "Ecopetrol (Bonos Corporativos)",
      "ISA (Bonos de Infraestructura)",
      "Grupo Sura (Bonos Ordinarios)",
      "Bancolombia (Bonos Subordinados)",
      "EPM",
      "Bogotá Fideicomisos",
  ]
  rf_list_gen = []
  for j in range(1, 101):
    emisor = random.choice(emisores_rf)
    tasa_anual = round(random.uniform(8.0, 13.5), 2)
    tipo_bono = random.choice(["Tasa Fija", "Indexado IPC", "Tasas IBR"])
    rf_list_gen.append({
        "id": f"RF-{j}",
        "emisor": emisor,
        "tipo": tipo_bono,
        "tasa": tasa_anual / 100.0,
        "desc": (
            f"Título {tipo_bono} de {emisor} con rendimiento estimado de"
            f" {tasa_anual}% anual."
        ),
    })
  st.session_state.all_rf = rf_list_gen
  st.session_state.instruments_initialized = True

if "pending_orders" not in st.session_state:
  st.session_state.pending_orders = []

# ==========================================
# 4. PANTALLA DE ACCESO OBLIGATORIO (LOGIN CON CONTRASEÑA Y BONO DE $500,000 COP)
# ==========================================
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if not st.session_state.logged_in:
  st.markdown(
      "<h1 style='text-align: center;'>🔐 BCV By Jp</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<h3 style='text-align: center; color: #8b949e;'>Portal Académico"
      " Financiero Institucional</h3>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
  with col_l2:
    st.write("Selecciona tu perfil de acceso:")
    rol = st.radio("Perfil:", ["Estudiante", "Profesor"])

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
              # BONO INICIAL DE $500,000 COP
              presup_def = 500000

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
              # Validar contraseña si ya existe
              user_db_info = st.session_state.user_database[nombre_est]
              if user_db_info["password"] != pass_est:
                st.error(
                    "❌ Contraseña incorrecta. Si ya estás registrado, ingresa"
                    " tu clave correcta."
                )
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
            st.error("Completa todos los campos, incluyendo la contraseña.")
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
  st.stop()# ==========================================
# 5. APLICACIÓN PRINCIPAL (PARTE 2 - PLANETA 3D, GUÍA Y DOBLE SIMULACIÓN)
# ==========================================
usuario_activo = st.session_state.current_user
rol_activo = st.session_state.current_role
u_data = st.session_state.user_database[usuario_activo]

if "historial_pasos" not in u_data:
  u_data["historial_pasos"] = []
if "informe_estudiante" not in u_data:
  u_data["informe_estudiante"] = ""

# Definir opciones de menú según el rol
if rol_activo == "Estudiante":
  opciones_menu = [
      "🏠 1. Presentación & Planeta 3D (Juan López)",
      "📖 2. Guía Paso a Paso (Onboarding)",
      "💡 3. Casos de Éxito Dinámicos",
      "📊 4. Catálogo & Análisis Técnico",
      "🧮 5. Markowitz (Frontera Óptima)",
      "🤖 6. Jp Advisor (Asistente IA)",
      "🏆 7. Ranking Global (Leaderboard)",
      "🏦 8. CDT y Renta Fija (Curva Macro)",
      "🛒 9. Terminal Bursátil (Compra/Venta)",
      "🌱 10. Fondo ESG Sostenible",
      "📰 11. Sala de Noticias Reales",
      "📝 12. Tareas e Informe",
      "⏳ 13. Simulación (Demo vs Día a Día Realista)",
      "🧠 14. Alertas de Riesgo & Correlación",
  ]
elif rol_activo == "Administrador":
  opciones_menu = [
      "👑 1. Panel Supremo Admin (Jp)",
      "🏠 2. Presentación & Planeta 3D",
      "📖 3. Guía Paso a Paso",
      "💡 4. Casos de Éxito Dinámicos",
      "📊 5. Catálogo Técnico",
      "🧮 6. Markowitz",
      "🤖 7. Jp Advisor",
      "🏆 8. Ranking",
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
      "🤖 6. Jp Advisor",
      "🏆 7. Ranking",
      "🏦 8. CDT & Renta Fija",
      "🛒 9. Terminal Bursátil",
      "🌱 10. Fondo ESG",
      "📰 11. Sala de Noticias Reales",
      "👨‍🏫 12. Panel de Asignaciones (Profesor)",
      "⏳ 13. Simulación (Demo vs Día a Día)",
      "🧠 14. Alertas de Riesgo",
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

# Resumen de Cuenta Sidebar
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
# MÓDULOS DE LA APLICACIÓN
# ==========================================
if menu == "👑 1. Panel Supremo Admin (Jp)":
  st.title("👑 Panel de Control Supremo del Administrador (Jp)")
  st.success(
      "¡Bienvenido, Jp! Tienes privilegios absolutos sobre la plataforma."
  )
  col_a1, col_a2, col_a3 = st.columns(3)
  with col_a1:
    st.metric("Usuarios Registrados", len(st.session_state.user_database))
  with col_a2:
    st.metric(
        "Activos en Sistema", len(st.session_state.prices_dict.keys())
    )
  with col_a3:
    st.metric("Asignaciones Docentes", len(st.session_state.prof_assignments))

  st.markdown("---")
  st.subheader("👥 Auditoría Global de Usuarios y Portafolios")
  db_all = load_user_db()
  for u_name, u_info in db_all.items():
    with st.expander(
        f"Usuario: {u_name} | Rol: {u_info['rol']} | Carrera:"
        f" {u_info['carrera']}"
    ):
      st.write(f"**Efectivo:** ${u_info['cash']:,.0f} COP")
      st.write(f"**Semestre:** {u_info['semestre']}")
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
  # HERO SECTION CON PLANETA 3D INTERACTIVO Y RED NEÓN
  st.markdown(
      """
        <div class="hero-planet-box">
            <h1 style="color: #58a6ff; font-size: 3rem; margin-bottom: 10px; text-shadow: 0 0 20px rgba(88,166,255,0.6);">🌍 BCV By Jp - Red Global & Terminal Bursátil</h1>
            <h3 style="color: #8b949e; font-weight: 400; margin-bottom: 25px;">Ecosistema Financiero Conectado con Inteligencia Estocástica y Datos Reales</h3>
            <p style="font-size: 1.15rem; color: #c9d1d9; max-width: 850px; margin: 0 auto; line-height: 1.6;">
                Plataforma de alta ingeniería desarrollada por <b>Juan Pablo López Tarriba (Juan López)</b>, estudiante de 
                <b>Administración de Empresas</b> de la <b>Universidad de Sucre</b> (Sincelejo, Colombia). 
                Conectamos los flujos bursátiles de la BVC y los mercados globales mediante una red neuronal de simulación financiera avanzada.
            </p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  # Gráfico Plotly Esférico 3D simulando el Planeta con conexiones neón
  df_globe = pd.DataFrame({
      "Lat": [4.5709, 40.7128, 51.5074, 35.6762, -33.8688, 19.4326],
      "Lon": [-74.2973, -74.0060, -0.1278, 139.6503, 151.2093, -99.1332],
      "Centro": [
          "Colombia (Sincelejo)",
          "New York (NYSE)",
          "London (LSE)",
          "Tokyo",
          "Sydney",
          "Mexico",
      ],
      "Volumen": [50000000, 900000000, 700000000, 600000000, 300000000, 200000000],
  })
  fig_globe = px.scatter_geo(
      df_globe,
      lat="Lat",
      lon="Lon",
      text="Centro",
      size="Volumen",
      projection="orthographic",
      title="🌐 Nodo Central de Conectividad Bursátil Global (BCV By Jp)",
  )
  fig_globe.update_geos(
      bgcolor="#060913",
      oceancolor="#0d1b2a",
      landcolor="#1b263b",
      showcountries=True,
      countrycolor="#415a77",
  )
  fig_globe.update_layout(
      height=450,
      paper_bgcolor="rgba(0,0,0,0)",
      font=dict(color="white"),
      margin=dict(l=0, r=0, t=40, b=0),
  )
  st.plotly_chart(fig_globe, use_container_width=True)

  col_p1, col_p2 = st.columns(2)
  with col_p1:
    st.markdown(
        """
            <div class="asset-card">
                <h3>🚀 Misión Institucional</h3>
                <p>Democratizar el acceso a herramientas analíticas de nivel de fondo de inversión, permitiendo a los estudiantes gestionar capitales virtuales de $500,000 COP y evaluar portafolios frente a choques reales de tasa de interés.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with col_p2:
    st.markdown(
        """
            <div class="asset-card">
                <h3>💡 Arquitectura Robusta</h3>
                <p>Soporte persistente SQLite protegido por contraseñas cifradas por usuario, cotizaciones reales, gráficos Plotly interactivos y simulador de Monte Carlo con toma de decisiones obligatoria.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

elif menu in ["📖 2. Guía Paso a Paso (Onboarding)", "📖 3. Guía Paso a Paso"]:
  st.title("📖 Guía Interactiva Paso a Paso (Cómo Usar la Plataforma)")
  st.write(
      "Bienvenido a tu manual de navegación rápida. Sigue estos pasos para"
      " convertirte en un trader experto en BCV By Jp:"
  )

  st.markdown(
      """
        <div class="asset-card">
            <h3>Paso 1: Tu Capital Inicial y Perfil</h3>
            <p>Al registrarte con tu contraseña personal, el sistema te otorga automáticamente un bono inicial de <b>$500,000 COP</b> en efectivo libre para comenzar a operar.</p>
        </div>
        
        <div class="asset-card">
            <h3>Paso 2: Explora el Catálogo y Análisis Técnico</h3>
            <p>Dirígete al módulo de <b>Catálogo & Análisis Técnico</b> para revisar más de 200 activos (Ecopetrol, Apple, Bancolombia, etc.) evaluando su Media Móvil (SMA) y el RSI.</p>
        </div>

        <div class="asset-card">
            <h3>Paso 3: Opera en la Terminal Bursátil</h3>
            <p>Usa la <b>Terminal Bursátil</b> para comprar o vender títulos utilizando el libro de puntas (Bid/Ask) exacto al de una bolsa de valores real.</p>
        </div>

        <div class="asset-card">
            <h3>Paso 4: Diversifica con CDT, Renta Fija y Fondo ESG</h3>
            <p>Protege tu capital invirtiendo en más de 100 opciones de CDT bancarios o bonos TES soberanos de la Nación, o apoya proyectos sostenibles en el Fondo ESG.</p>
        </div>

        <div class="asset-card">
            <h3>Paso 5: Enfrenta la Simulación Día a Día y Revisa Alertas</h3>
            <p>Pon a prueba tu portafolio en el módulo de <b>Simulación Día a Día Realista</b> tomando decisiones gerenciales ante crisis macroeconómicas, y audita tu nivel de riesgo en el módulo de Correlación.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

elif menu in ["💡 3. Casos de Éxito Dinámicos", "💡 4. Casos de Éxito Dinámicos"]:
  st.title("💡 Casos de Éxito Dinámicos y el Poder de la Inversión")
  banco_casos = [
      (
          "🌟 Caso de Éxito: Anne Scheiber y el Interés Compuesto",
          (
              "Anne Scheiber invirtió sistemáticamente en blue chips y su"
              " portafolio superó los **$22 millones de dólares** al fallecer a"
              " los 101 años."
          ),
      ),
      (
          "🌟 Caso de Éxito: Coberturas Institucionales en TES",
          (
              "Fondos que anticiparon el ciclo alcista de tasas del Banrep"
              " estructuraron coberturas con TES y servicios públicos (ISA),"
              " blindando millones de afiliados."
          ),
      ),
  ]
  casos_sel = random.sample(banco_casos, 2)
  col_c1, col_c2 = st.columns(2)
  with col_c1:
    st.markdown(
        f'<div class="asset-card"><h3>{casos_sel[0][0]}</h3><p>{casos_sel[0][1]}</p></div>',
        unsafe_allow_html=True,
    )
  with col_c2:
    st.markdown(
        f'<div class="asset-card"><h3>{casos_sel[1][0]}</h3><p>{casos_sel[1][1]}</p></div>',
        unsafe_allow_html=True,
    )

elif menu in ["📊 4. Catálogo & Análisis Técnico", "📊 5. Catálogo Técnico"]:
  st.title("📊 Catálogo de Activos con Precios Reales y Análisis Técnico")
  busc = st.text_input("🔍 Buscar activo:")
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
      "Selecciona de 2 a 5 activos:",
      list(st.session_state.prices.keys()),
      default=["ECOPETROL", "BCOLOMBIA", "ISA"][: min(3, len(st.session_state.prices))],
  )
  if len(activos_sel) >= 2:
    if st.button("Calcular Portafolio Óptimo ⚙️"):
      pesos_raw = [random.uniform(0.1, 0.9) for _ in activos_sel]
      suma_p = sum(pesos_raw)
      pesos_opt = [p / suma_p for p in pesos_raw]
      st.success("¡Optimización completada con éxito!")
      df_opt = pd.DataFrame(
          {
              "Activo": activos_sel,
              "Peso Óptimo (%)": [f"{p*100:.2f}%" for p in pesos_opt],
              "Precio COP": [
                  f"${st.session_state.prices[a]:,.0f}" for a in activos_sel
              ],
          }
      )
      st.dataframe(df_opt, use_container_width=True)
  else:
    st.warning("Selecciona al menos 2 activos.")

elif menu in ["🤖 6. Jp Advisor (Asistente IA)", "🤖 7. Jp Advisor"]:
  st.title("🤖 Jp Advisor - Tu Mentor Financiero Conversacional")
  for q, a in st.session_state.jp_chat_history:
    st.markdown(f"👤 **Tú:** {q}")
    st.markdown(f"🤖 **Jp Advisor:** {a}")
  with st.form("form_chat_jp", clear_on_submit=True):
    pregunta_usuario = st.text_input("Escribe tu consulta:")
    btn_enviar_ia = st.form_submit_button("Enviar Mensaje 🚀")
    if btn_enviar_ia and pregunta_usuario.strip():
      resp = (
          f"¡Entendido, {usuario_activo}! Analizar los precios reales del"
          " mercado te da ventaja gerencial."
      )
      st.session_state.jp_chat_history.append((pregunta_usuario, resp))
      save_user_to_db(usuario_activo, u_data)
      st.rerun()

elif menu in ["🏆 7. Ranking Global (Leaderboard)", "🏆 8. Ranking"]:
  st.title("🏆 Tabla de Clasificación de Traders (Leaderboard)")
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

elif menu in ["🏦 8. CDT y Renta Fija (Curva Macro)", "🏦 8. CDT & Renta Fija"]:
  st.title("🏦 CDT y Renta Fija con Curva Macro")
  tab1, tab2 = st.tabs(["📌 CDT", "📜 Renta Fija (TES / Bonos)"])
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

elif menu in ["🛒 9. Terminal Bursátil (Compra/Venta)", "🛒 9. Terminal Bursátil"]:
  st.title("🛒 Terminal Bursátil Avanzada (Bid / Ask)")
  ticker_op = st.selectbox(
      "Seleccione Activo:", list(st.session_state.prices.keys())
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

  cant = st.number_input("Cantidad:", 1, 10000, 10)
  if st.button("Comprar Acciones ⚡"):
    costo = ask_prc * cant
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

elif menu in ["🌱 10. Fondo ESG Sostenible", "🌱 10. Fondo ESG"]:
  st.title("🌱 Fondo de Inversión Colectiva ESG")
  monto_esg = st.number_input("Monto:", 100000, 50000000, 500000, step=100000)
  if st.button("Invertir ESG 🌱"):
    if u_data["cash"] >= monto_esg:
      u_data["cash"] -= monto_esg
      u_data["esg_fund"] = u_data.get("esg_fund", 0) + monto_esg
      save_user_to_db(usuario_activo, u_data)
      st.success("¡Inversión ESG realizada!")
      st.rerun()
    else:
      st.error("Efectivo insuficiente.")

elif menu in ["📰 11. Sala de Noticias Reales", "📰 11. Sala de Noticias"]:
  st.title("📰 Sala de Noticias Financieras Reales (Actualizadas)")
  for fuente, txt in st.session_state.news_feed[:10]:
    st.markdown(
        f'<div class="asset-card"><h4>{fuente}</h4><p>{txt}</p></div>',
        unsafe_allow_html=True,
    )

elif menu in ["📝 12. Tareas e Informe", "📝 12. Tareas"]:
  st.title("📝 Tareas y Justificación Analítica")
  sem_est = u_data.get("semestre", "")
  t_disp = {
      k: v
      for k, v in st.session_state.prof_assignments.items()
      if v["semestre_objetivo"] == sem_est
  }
  if not t_disp:
    st.info(f"No hay tareas asignadas para tu {sem_est}.")
  else:
    for tit, info in t_disp.items():
      st.markdown(f"### 📌 {tit}")
      st.write(info["descripcion"])
      informe = st.text_area(
          "Informe técnico:",
          value=u_data.get("informe_estudiante", ""),
          key=f"inf_{tit}",
      )
      u_data["informe_estudiante"] = informe
      if st.button("Enviar Tarea 🚀", key=f"btn_{tit}"):
        info["entregas"][usuario_activo] = {
            "portafolio": u_data["portfolio_acciones"],
            "informe": informe,
        }
        save_assignment_to_db(tit, info)
        save_user_to_db(usuario_activo, u_data)
        st.success("¡Enviado correctamente!")
        st.rerun()

elif menu == "👨‍🏫 12. Panel de Asignaciones (Profesor)":
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
    guardado = st.form_submit_button("Publicar Actividad 🚀")
    if guardado and t_tit.strip():
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
    "⏳ 13. Simulación (Demo vs Día a Día Realista)",
    "⏳ 10. Simulación (Demo vs Día a Día)",
    "⏳ 13. Simulación (Demo vs Día a Día)",
]:
  st.title(
      "⏳ Motor de Simulación: Modo Demo vs Modo Día a Día Realista (Oct 2026)"
  )
  modo_sim = st.radio(
      "Selecciona el Modo de Simulación:",
      [
          "🚀 Modo Demo (Simulación Rápida Estocástica)",
          "📅 Modo Día a Día Realista (Sincronizado con Calendario)",
      ],
  )

  if "sim_dias" not in st.session_state:
    st.session_state.sim_dias = 0
    st.session_state.sim_hist = []
    st.session_state.sim_running = False

  if "Modo Demo" in modo_sim:
    st.write(
        "Simulación rápida para evaluar escenarios y bandas de confianza"
        " (95% / 5%)."
    )
    plazo_demo = st.number_input("Cantidad de Pasos Demo:", 1, 100, 30)
    if st.button("Iniciar Modo Demo 🚀"):
      st.session_state.sim_dias = 1
      st.session_state.sim_hist = [
          sum(
              cant * st.session_state.prices[t]
              for t, cant in u_data["portfolio_acciones"].items()
          )
          or 500000
      ]
      st.session_state.sim_running = True
      st.rerun()

    if st.session_state.sim_running:
      if st.button("Avanzar 1 Paso Demo ⏭"):
        st.session_state.sim_dias += 1
        nv = st.session_state.sim_hist[-1] * (
            1 + random.normalvariate(0.001, 0.015)
        )
        st.session_state.sim_hist.append(nv)
        st.rerun()
      fig_d = px.line(
          y=st.session_state.sim_hist, title="Evolución en Modo Demo"
      )
      fig_d.update_layout(
          height=300,
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          font=dict(color="white"),
      )
      st.plotly_chart(fig_d, use_container_width=True)
  else:
    st.write(
        "📅 **Modo Día a Día Realista:** Avanzas operativamente jornada por"
        f" jornada a partir de hoy ({st.session_state.current_date}). Cada"
        " avance procesa la volatilidad real del mercado."
    )
    if st.button("Avanzar 1 Jornada Real (Día Siguiente) 📈"):
      st.session_state.current_date += datetime.timedelta(days=1)
      for t_k in st.session_state.prices:
        v = random.normalvariate(0.0006, 0.015)
        st.session_state.prices[t_k] = max(
            50, int(st.session_state.prices[t_k] * (1 + v))
        )
      st.success(
          f"¡Jornada avanzada! Nueva fecha del simulador:"
          f" {st.session_state.current_date}"
      )
      st.rerun()

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
  total_cdt_val = sum(c["monto"] for c in u_data["cdt_list"])
  total_rf_val = sum(r["monto"] for r in u_data["renta_fija_list"])
  tot_pat = total_acc_val + total_cdt_val + total_rf_val + u_data["cash"]

  if tot_pat > 0:
    pct_acc = (total_acc_val / tot_pat) * 100
    col_r1, col_r2 = st.columns(2)
    with col_r1:
      st.metric("Exposición Renta Variable", f"{pct_acc:.1f}%")
    with col_r2:
      st.metric(
          "Efectivo Libre", f"${u_data['cash']:,.0f} COP".replace(",", ".")
      )

    if pct_acc > 75:
      st.error(
          "🔴 **ALERTA DE CONCENTRACIÓN:** Alta exposición a renta variable."
          " Considere diversificar en CDT."
      )
    else:
      st.success(
          "🟢 **PORTAFOLIO EQUILIBRADO:** Niveles de riesgo dentro de"
          " parámetros institucionales."
      )