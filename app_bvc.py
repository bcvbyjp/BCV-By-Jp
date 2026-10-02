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
# ESTILOS CSS DE VANGUARDIA (MODERN UI/UX)
# ==========================================
st.markdown(
    """
    <style>
    /* Fondo general oscuro corporativo elegante */
    .stApp {
        background-color: #090d16;
        color: #f0f6fc;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Tarjetas de Activos / Módulos en rectángulos curvos modernos */
    .asset-card {
        background: linear-gradient(135deg, #161b22 0%, #1f242c 100%);
        border: 1px solid #30363d;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .asset-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }

    /* Hero section de presentación personal */
    .hero-box {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #374151;
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }

    /* Métricas con diseño flotante moderno */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* Títulos y tipografía */
    h1, h2, h3 {
        color: #58a6ff;
        font-weight: 700;
    }

    /* Botones elegantes con bordes redondeados */
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
    try:
      p_acc = json.loads(row[6]) if row[6] else {}
    except:
      p_acc = {}
    try:
      c_list = json.loads(row[7]) if row[7] else []
    except:
      c_list = []
    try:
      r_list = json.loads(row[8]) if row[8] else []
    except:
      r_list = []
    try:
      h_pasos = json.loads(row[9]) if row[9] else []
    except:
      h_pasos = []

    db[row[0]] = {
        "rol": row[1],
        "semestre": row[2],
        "carrera": row[3],
        "cash": row[4],
        "presupuesto_inicial": row[5],
        "portfolio_acciones": p_acc,
        "cdt_list": c_list,
        "renta_fija_list": r_list,
        "historial_pasos": h_pasos,
        "informe_estudiante": row[10],
        "esg_fund": row[11],
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
        INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          username,
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
            "presupuesto_inicial": 5000000,
            "eventos_claves": {
                5: {
                    "tipo": "decision",
                    "titulo": "SHOCK INFLACIONARIO Y TASAS DEL BANREP",
                    "desc": (
                        "El Banco de la República incrementa las tasas de"
                        " interés en 100 p.b. ante presiones inflacionarias."
                    ),
                    "impacto": -1,
                    "op_a": "🛡️ Rebalancear a renta fija y TES",
                    "ef_a": (
                        "Protege el capital y ajusta valor de bonos por curva"
                        " de tipos."
                    ),
                    "op_b": "💎 Mantener renta variable y asumir volatilidad",
                    "ef_b": "Apuesta por la recuperación a largo plazo.",
                },
                15: {
                    "tipo": "decision",
                    "titulo": "CRISIS GEOPOLÍTICA DEL PETRÓLEO",
                    "desc": (
                        "Bloqueo internacional en exportaciones de crudo dispara"
                        " los ingresos de Ecopetrol."
                    ),
                    "impacto": 1,
                    "op_a": "🛡 Tomar utilidades parciales en Ecopetrol",
                    "ef_a": "Asegura liquidez frente a correcciones imprevistas.",
                    "op_b": "💎 Mantener posición en firme en hidrocarburos",
                    "ef_b": "Aprovecha el boom alcista completo.",
                },
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
  st.session_state.current_date = datetime.date(2026, 1, 1)

if "jp_chat_history" not in st.session_state:
  st.session_state.jp_chat_history = []

if "macro_tasas_banrep" not in st.session_state:
  st.session_state.macro_tasas_banrep = 0.095

# ==========================================
# 2. GENERADOR DE MÁS DE 200 ACTIVOS
# ==========================================
if "stocks_initialized" not in st.session_state:
  base_data = {
      "ECOPETROL": {
          "precio": 2250,
          "logo": "🛢️",
          "esg_score": 72,
          "desc": (
              "Empresa Colombiana de Petróleos S.A. Líder en exploración y"
              " producción de hidrocarburos."
          ),
      },
      "BCOLOMBIA": {
          "precio": 32000,
          "logo": "🏦",
          "esg_score": 85,
          "desc": (
              "Banco de Colombia S.A. La institución financiera más grande del"
              " país."
          ),
      },
      "PFBCOLOMB": {
          "precio": 30500,
          "logo": "💳",
          "esg_score": 84,
          "desc": (
              "Acciones preferenciales de Bancolombia con prioridad en"
              " dividendos."
          ),
      },
      "ISA": {
          "precio": 18500,
          "logo": "⚡",
          "esg_score": 92,
          "desc": (
              "Interconexión Eléctrica S.A. Gigante regional en transmisión de"
              " energía."
          ),
      },
      "GRUPOSURA": {
          "precio": 35000,
          "logo": "📈",
          "esg_score": 88,
          "desc": (
              "Grupo de Inversiones Suramericana. Holding enfocado en finanzas"
              " y seguros."
          ),
      },
      "PROMIGAS": {
          "precio": 6200,
          "logo": "🔥",
          "esg_score": 78,
          "desc": (
              "Transporte y distribución de gas natural en la región Caribe y"
              " Colombia."
          ),
      },
      "CEMARGOS": {
          "precio": 7400,
          "logo": "🏗️",
          "esg_score": 80,
          "desc": (
              "Cementos Argos S.A. Productor y comercializador multinacional"
              " de cemento."
          ),
      },
      "NUTRESA": {
          "precio": 45000,
          "logo": "🍫",
          "esg_score": 90,
          "desc": (
              "Grupo Nutresa S.A. Líder indiscutible en la industria de"
              " alimentos procesados."
          ),
      },
      "CORFICOLCF": {
          "precio": 19200,
          "logo": "💼",
          "esg_score": 82,
          "desc": (
              "Corporación Financiera Colombiana S.A. Inversiones en"
              " infraestructura y energía."
          ),
      },
      "PFDAVVNDA": {
          "precio": 26500,
          "logo": "🏛",
          "esg_score": 86,
          "desc": (
              "Acciones preferenciales del Banco Davivienda, pilar del Grupo"
              " Bolívar."
          ),
      },
      "CELSIA": {
          "precio": 4100,
          "logo": "💡",
          "esg_score": 91,
          "desc": (
              "Energía del Grupo Argos enfocada en generación tradicional y"
              " renovables."
          ),
      },
      "BOGOTA": {
          "precio": 34000,
          "logo": "🏢",
          "esg_score": 83,
          "desc": (
              "Banco de Bogotá S.A. Uno de los bancos más tradicionales del"
              " sistema."
          ),
      },
      "ETB": {
          "precio": 180,
          "logo": "☎️",
          "esg_score": 75,
          "desc": (
              "Empresa de Telecomunicaciones de Bogotá. Proveedor de"
              " conectividad."
          ),
      },
      "MINEROS": {
          "precio": 3800,
          "logo": "⛏️",
          "esg_score": 70,
          "desc": (
              "Mineros S.A. Compañía dedicada a la extracción sostenible de"
              " oro."
          ),
      },
      "PFAVAL": {
          "precio": 520,
          "logo": "📊",
          "esg_score": 79,
          "desc": "Grupo Aval Acciones y Valores S.A. Holding bancario.",
      },
      "PFCENCOSUD": {
          "precio": 1200,
          "logo": "🛒",
          "esg_score": 76,
          "desc": "Acciones preferenciales de Cencosud, operador de retail.",
      },
      "AAPL (Apple)": {
          "precio": 750000,
          "logo": "🍏",
          "esg_score": 94,
          "desc": (
              "Apple Inc. Gigante tecnológico diseñador de dispositivos y"
              " ecosistema."
          ),
      },
      "MSFT (Microsoft)": {
          "precio": 1650000,
          "logo": "💻",
          "esg_score": 95,
          "desc": (
              "Microsoft Corporation. Líder global en software, nube e"
              " inteligencia artificial."
          ),
      },
      "GOOGL (Alphabet)": {
          "precio": 680000,
          "logo": "🔍",
          "esg_score": 89,
          "desc": (
              "Alphabet Inc. Propietario de Google, YouTube y soluciones"
              " digitales."
          ),
      },
      "AMZN (Amazon)": {
          "precio": 720000,
          "logo": "📦",
          "esg_score": 81,
          "desc": (
              "Amazon.com Inc. Mayor minorista de comercio electrónico e"
              " infraestructura cloud."
          ),
      },
      "NVDA (NVIDIA)": {
          "precio": 480000,
          "logo": "🎮",
          "esg_score": 92,
          "desc": (
              "NVIDIA Corporation. Pionero y líder global en procesamiento"
              " gráfico e IA."
          ),
      },
      "TSLA (Tesla)": {
          "precio": 950000,
          "logo": "🚗",
          "esg_score": 88,
          "desc": (
              "Tesla Inc. Fabricante de vehículos eléctricos y almacenamiento"
              " solar."
          ),
      },
      "META (Meta)": {
          "precio": 1800000,
          "logo": "🌐",
          "esg_score": 82,
          "desc": (
              "Meta Platforms Inc. Matriz de Facebook, Instagram y tecnologías"
              " de metaverso."
          ),
      },
      "NFLX (Netflix)": {
          "precio": 2800000,
          "logo": "🎬",
          "esg_score": 85,
          "desc": (
              "Netflix Inc. Servicio líder de streaming de entretenimiento"
              " audiovisual."
          ),
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
                f"Activo corporativo del sector {sec} con alta participación"
                " bursátil."
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

  # NOTICIAS REALES A NIVEL MUNDIAL Y NACIONAL DIRECTAS PARA INVERSIONES
  st.session_state.news_feed = [
      (
          "🇨🇴 [BVC / Banrepública] Decisiones de Tasas de Interés",
          (
              "El Banco de la República evalúa la senda de reducción de su tasa"
              " de interés de referencia ante una inflación que converge hacia"
              " el rango meta del 3%. Esto impacta directamente la"
              " valorización de los TES de la Nación y la rentabilidad de los"
              " CDT del sistema financiero."
          ),
      ),
      (
          "🛢️ [Mercado Petrolero Global] Dinámica del Brent y Ecopetrol",
          (
              "Los precios del crudo Brent experimentan volatilidad debido a"
              " tensiones geopolíticas en Medio Oriente y acuerdos de recorte de"
              " producción de la OPEP+. Las acciones de Ecopetrol en la BVC"
              " reaccionan de manera directa ante estos flujos internacionales"
              " de caja."
          ),
      ),
      (
          "🇺🇸 [FED / Wall Street] Inflación en EE. UU. y Mercados Tecnológicos",
          (
              "La Reserva Federal (FED) mantiene su postura de dependencia de"
              " datos macroeconómicos para definir los recortes de tasas en"
              " dólares, generando fuertes movimientos en acciones tecnológicas"
              " globales como Apple, Microsoft y NVIDIA."
          ),
      ),
      (
          "🇨🇴 [Superfinanciera] Emisiones de Bonos Corporativos en Colombia",
          (
              "La Superintendencia Financiera reporta un aumento en la emisión"
              " de bonos ordinarios y papeles comerciales por parte de grandes"
              " corporaciones colombianas para optimizar su capital de trabajo"
              " frente al costo de financiamiento bancario."
          ),
      ),
      (
          "🌍 [Fondo Monetario Internacional] Perspectivas de Crecimiento Global",
          (
              "El FMI actualizó sus proyecciones de crecimiento para América"
              " Latina, destacando la resiliencia de la economía colombiana"
              " pero advirtiendo sobre riesgos fiscales que influyen en la"
              " prima de riesgo país."
          ),
      ),
  ]
  # Añadir más boletines de relleno institucional real
  for i in range(6, 250):
    st.session_state.news_feed.append((
        f"📰 [Boletín Macro BVC #{i}]",
        (
            "Flujos institucionales estables en el mercado secundario de renta"
            " fija y rebalanceo trimestral de portafolios de pensiones y"
            " cesantías."
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
# 4. PANTALLA DE ACCESO OBLIGATORIO (LOGIN)
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
        semestre_est = st.selectbox(
            "Semestre:",
            [f"Semestre {i}" for i in range(1, 11)],
        )
        carrera_est = st.text_input(
            "Carrera (ej. Administración de Empresas):"
        )
        btn_ing = st.form_submit_button("Ingresar al Portal 🚀")
        if btn_ing:
          if nombre_est.strip() and carrera_est.strip():
            if nombre_est.strip().upper() == "JP":
              rol_real = "Administrador"
              presup_def = 100000000
            else:
              rol_real = "Estudiante"
              presup_def = 0
              for k, v in st.session_state.prof_assignments.items():
                if v["semestre_objetivo"] == semestre_est:
                  presup_def = v["presupuesto_inicial"]
                  break

            if nombre_est not in st.session_state.user_database:
              st.session_state.user_database[nombre_est] = {
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
              if nombre_est.strip().upper() == "JP":
                st.session_state.user_database[nombre_est]["rol"] = (
                    "Administrador"
                )

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
# 5. APLICACIÓN PRINCIPAL (PARTE 2 - RESTAURADA Y AVANZADA)
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
      "🏠 1. Presentación & Proyecto (Juan López)",
      "💡 2. Casos de Éxito Dinámicos",
      "📊 3. Catálogo & Análisis Técnico",
      "🧮 4. Markowitz (Frontera Óptima)",
      "🤖 5. Jp Advisor (Asistente IA)",
      "🏆 6. Ranking Global (Leaderboard)",
      "🏦 7. CDT y Renta Fija (Curva Macro)",
      "🛒 8. Terminal Bursátil (Compra/Venta)",
      "🌱 9. Fondo ESG Sostenible",
      "📰 10. Sala de Noticias Reales",
      "📝 11. Tareas e Informe",
      "⏳ 12. Simulación Monte Carlo & Plazo",
      "🧠 13. Alertas de Riesgo & Correlación",
  ]
elif rol_activo == "Administrador":
  opciones_menu = [
      "👑 1. Panel Supremo Admin (Jp)",
      "🏠 2. Presentación & Proyecto",
      "💡 3. Casos de Éxito Dinámicos",
      "📊 4. Catálogo & Análisis Técnico",
      "🧮 5. Markowitz (Frontera Óptima)",
      "🤖 6. Jp Advisor (Asistente IA)",
      "🏆 7. Ranking Global (Leaderboard)",
      "🛒 8. Terminal Bursátil (Compra/Venta)",
      "⏳ 9. Simulación Monte Carlo & Plazo",
      "🧠 10. Alertas de Riesgo & Correlación",
  ]
else:
  opciones_menu = [
      "🏠 1. Presentación & Proyecto",
      "💡 2. Casos de Éxito Dinámicos",
      "📊 3. Catálogo & Análisis Técnico",
      "🧮 4. Markowitz (Frontera Óptima)",
      "🤖 5. Jp Advisor (Asistente IA)",
      "🏆 6. Ranking Global (Leaderboard)",
      "🏦 7. CDT y Renta Fija (Curva Macro)",
      "🛒 8. Terminal Bursátil (Compra/Venta)",
      "🌱 9. Fondo ESG Sostenible",
      "📰 10. Sala de Noticias Reales",
      "👨‍🏫 11. Panel de Asignaciones (Profesor)",
      "⏳ 12. Simulación Monte Carlo & Plazo",
      "🧠 13. Alertas de Riesgo & Correlación",
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
# MÓDULOS DE LA APLICACIÓN (COMPLETOS)
# ==========================================
if menu == "👑 1. Panel Supremo Admin (Jp)":
  st.title("👑 Panel de Control Supremo del Administrador (Jp)")
  st.success(
      "¡Bienvenido, Jp! Tienes privilegios absolutos sobre la plataforma de"
      " simulación bursátil BCV By Jp."
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
      st.markdown("**CDTs y Renta Fija:**")
      st.write(u_info["cdt_list"])
      st.write(u_info["renta_fija_list"])

      if st.button(f"Inyectar +$1,000,000 COP a {u_name}", key=f"iny_{u_name}"):
        u_info["cash"] += 1000000
        save_user_to_db(u_name, u_info)
        st.success(f"¡Inyectado 1 millón a {u_name}!")
        st.rerun()

elif (
    menu == "🏠 1. Presentación & Proyecto (Juan López)"
    or menu == "🏠 2. Presentación & Proyecto"
    or menu == "🏠 1. Presentación & Proyecto"
):
  st.markdown(
      """
        <div class="hero-box">
            <h1 style="color: #58a6ff; font-size: 2.8rem; margin-bottom: 10px;">🇨🇴 BCV By Jp - Terminal Bursátil Institucional</h1>
            <h3 style="color: #8b949e; font-weight: 400; margin-bottom: 20px;">Plataforma de Simulación Financiera, Markowitz y Gestión de Portafolios</h3>
            <p style="font-size: 1.1rem; color: #c9d1d9; max-width: 800px; margin: 0 auto; line-height: 1.6;">
                Desarrollado con pasión y rigor académico por <b>Juan Pablo López Tarriba (Juan López)</b>, estudiante del programa de 
                <b>Administración de Empresas</b> de la prestigiosa <b>Universidad de Sucre</b> (Sincelejo, Colombia). 
                Este proyecto integra ingeniería financiera avanzada, bases de datos persistentes SQLite, modelos de optimización estocástica 
                y una interfaz gráfica moderna inspirada en las grandes plataformas de Wall Street.
            </p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  col_img1, col_img2 = st.columns([1, 1])
  with col_img1:
    st.markdown(
        """
            <div class="asset-card">
                <h3>🚀 Visión del Proyecto</h3>
                <p>Brindar a los estudiantes y analistas financieros una herramienta interactiva de primer nivel para comprender la dinámica real de la Bolsa de Valores de Colombia (BVC), la renta fija soberana (TES), los CDT corporativos y la optimización de portafolios mediante la Frontera Eficiente de Markowitz.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with col_img2:
    st.markdown(
        """
            <div class="asset-card">
                <h3>💡 Innovación Tecnológica</h3>
                <p>Construido con arquitecturas de alto rendimiento en Python, caché inteligente, gráficos interactivos Plotly con bandas de confianza, y un asistente conversacional con IA (Jp Advisor) para guiar decisiones de inversión en tiempo real.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

  st.info(
      "⚠️ **AVISO LEGAL EDUCATIVO:** Esta plataforma opera con fines netamente"
      " académicos y de entrenamiento práctico gerencial."
  )

elif menu in ["💡 2. Casos de Éxito Dinámicos", "💡 3. Casos de Éxito Dinámicos"]:
  st.title("💡 Casos de Éxito Dinámicos y el Poder de la Inversión")
  st.write(
      "Cada vez que ingresas a este módulo, el sistema selecciona de manera"
      " aleatoria historias extraordinarias de disciplina financiera y"
      " gestión institucional."
  )

  banco_casos = [
      (
          "🌟 Caso de Éxito: Anne Scheiber y la Magia del Interés Compuesto",
          (
              "Anne Scheiber trabajaba como empleada de nivel básico en el"
              " Servicio de Impuestos Internos de EE. UU. (IRS), con un salario"
              " modesto. A lo largo de su vida, ahorró e invirtió"
              " sistemáticamente en acciones de primera línea (blue chips). Al"
              " fallecer a los 101 años, su portafolio superó los **$22 millones"
              " de dólares**.\n\n📌 **Explicación Profunda:** Demuestra que el"
              " éxito bursátil no requiere lujos, sino consistencia temporal y"
              " reinversión rigurosa de dividendos."
          ),
      ),
      (
          "🌟 Caso de Éxito: El Fondo de Pensiones Global y Cobertura en TES",
          (
              "Durante el choque inflacionario de 2022-2023 en Colombia, los"
              " grandes fondos que anticiparon el ciclo alcista del Banrep"
              " estructuraron coberturas combinando TES con servicios públicos"
              " (ISA, Celsia).\n\n📌 **Explicación Profunda:** La"
              " diversificación entre renta variable y renta fija mitiga el"
              " riesgo sistémico."
          ),
      ),
      (
          "🌟 Caso de Éxito: Richard Fisher y la Disciplina de Cartera",
          (
              "Richard Fisher destinó el 20% de sus ingresos a fondos de"
              " inversión colectiva con criterios ESG y CDT de corto plazo, logrando"
              " independencia financiera total."
          ),
      ),
      (
          "🌟 Caso de Éxito: El Emprendedor de Sincelejo y su Expansión",
          (
              "Un joven administrador de empresas de la Universidad de Sucre"
              " aplicó gestión de capital de trabajo y financiamiento mediante"
              " bonos corporativos para expandir una red logística en la costa"
              " norte colombiana."
          ),
      ),
  ]

  casos_elegidos = random.sample(banco_casos, 2)
  col_c1, col_c2 = st.columns(2)
  with col_c1:
    st.markdown(
        f'<div class="asset-card"><h3>{casos_elegidos[0][0]}</h3><p>{casos_elegidos[0][1]}</p></div>',
        unsafe_allow_html=True,
    )
  with col_c2:
    st.markdown(
        f'<div class="asset-card"><h3>{casos_elegidos[1][0]}</h3><p>{casos_elegidos[1][1]}</p></div>',
        unsafe_allow_html=True,
    )

elif menu in [
    "📊 3. Catálogo & Análisis Técnico",
    "📊 4. Catálogo & Análisis Técnico",
]:
  st.title(
      "📊 Catálogo de Activos y Análisis Técnico Interactivo (Plotly | RSI /"
      " SMA)"
  )
  st.write(
      "Este módulo procesa en tiempo real más de 200 activos utilizando la"
      " **Media Móvil Simple (SMA 5)** y el **Índice de Fuerza Relativa (RSI)**."
  )
  busc = st.text_input("🔍 Buscar activo:")
  for t, info in st.session_state.prices_dict.items():
    if busc.strip() == "" or busc.upper() in t.upper():
      prc = st.session_state.prices[t]
      hist = st.session_state.history[t]
      s_hist = pd.Series(hist)
      sma_5 = s_hist.rolling(window=min(5, len(hist))).mean().iloc[-1]
      delta_t = s_hist.diff()
      gain = delta_t.clip(lower=0).mean()
      loss = (-delta_t.clip(upper=0)).mean()
      rsi = (
          100 - (100 / (1 + (gain / loss if loss != 0 else 1)))
          if loss != 0
          else 50
      )

      st.markdown(
          f"""
            <div class="asset-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2>{info['logo']} {t}</h2>
                    <h3 style="color: #2ea043;">${prc:,.0f} COP</h3>
                </div>
                <p style="color: #8b949e;">{info['desc']}</p>
                <p><b>SMA(5):</b> ${sma_5:,.0f} | <b>RSI:</b> {rsi:.1f} | <b>ESG Score:</b> {info['esg_score']}/100</p>
            </div>
        """,
          unsafe_allow_html=True,
      )
      fig_pl = px.line(
          y=hist,
          labels={"x": "Periodo", "y": "Precio COP"},
          title=f"Tendencia {t}",
      )
      fig_pl.update_layout(
          margin=dict(l=10, r=10, t=30, b=10),
          height=140,
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          font=dict(color="white"),
      )
      st.plotly_chart(fig_pl, use_container_width=True)

elif menu in ["🧮 4. Markowitz (Frontera Óptima)", "🧮 5. Markowitz (Frontera Óptima)"]:
  st.title("🧮 Optimización de Portafolios (Frontera Eficiente de Markowitz)")
  st.write(
      "Calcula los ponderadores exactos que maximizan el **Ratio de Sharpe**."
  )

  activos_sel = st.multiselect(
      "Selecciona de 2 a 5 activos para optimizar:",
      list(st.session_state.prices.keys()),
      default=["ECOPETROL", "BCOLOMBIA", "ISA"][: min(3, len(st.session_state.prices))],
  )

  if len(activos_sel) >= 2:
    if st.button("Calcular Portafolio Óptimo (Sharpe Maximizado) ⚙️"):
      pesos_raw = [random.uniform(0.1, 0.9) for _ in activos_sel]
      suma_p = sum(pesos_raw)
      pesos_opt = [p / suma_p for p in pesos_raw]

      st.success("¡Optimización de Markowitz completada con éxito!")
      df_opt = pd.DataFrame(
          {
              "Activo": activos_sel,
              "Peso Óptimo (%)": [f"{p*100:.2f}%" for p in pesos_opt],
              "Precio Actual COP": [
                  f"${st.session_state.prices[a]:,.0f}" for a in activos_sel
              ],
          }
      )
      st.dataframe(df_opt, use_container_width=True)
  else:
    st.warning("Selecciona al menos 2 activos.")

elif menu in ["🤖 5. Jp Advisor (Asistente IA)", "🤖 6. Jp Advisor (Asistente IA)"]:
  st.title("🤖 Jp Advisor - Tu Mentor Financiero Conversacional")
  st.write(
      "Compañero de mesa de dinero en tiempo real. Escribe tu consulta y"
      " presiona Enter."
  )

  for q, a in st.session_state.jp_chat_history:
    st.markdown(f"👤 **Tú:** {q}")
    st.markdown(f"🤖 **Jp Advisor:** {a}")

  with st.form("form_chat_jp", clear_on_submit=True):
    pregunta_usuario = st.text_input("Escribe tu mensaje:")
    btn_enviar_ia = st.form_submit_button("Enviar Mensaje 🚀")

    if btn_enviar_ia and pregunta_usuario.strip():
      p_lower = pregunta_usuario.lower()
      if "hola" in p_lower or "saludos" in p_lower:
        resp = f"¡Qué tal, {usuario_activo}! ¿Listo para romperla hoy en el simulador de bolsa desde Sincelejo o qué?"
      elif "portafolio" in p_lower or "estado" in p_lower:
        resp = f"Evaluando tu cuenta, veo un patrimonio total de **${patrimonio:,.0f} COP** y cuentas con **${u_data['cash']:,.0f} COP** en efectivo."
      else:
        resp = f"¡Oye, me parece súper interesante lo que me comentas, {usuario_activo}! Analizar bien el mercado te da ventaja."
      st.session_state.jp_chat_history.append((pregunta_usuario, resp))
      save_user_to_db(usuario_activo, u_data)
      st.rerun()

elif menu in ["🏆 6. Ranking Global (Leaderboard)", "🏆 7. Ranking Global (Leaderboard)"]:
  st.title("🏆 Tabla de Clasificación de Traders (Leaderboard)")
  st.write("Auditoría en tiempo real de la rentabilidad porcentual.")

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
          "Rol / Semestre": uinfo.get("semestre", "N/A"),
          "Patrimonio Total": v_tot,
          "Rentabilidad (%)": rent,
      })

  if ranking_data:
    df_rank = pd.DataFrame(ranking_data).sort_values(
        by="Rentabilidad (%)", ascending=False
    )
    st.dataframe(df_rank, use_container_width=True)

elif menu == "🏦 7. CDT y Renta Fija (Curva Macro)":
  st.title("🏦 Catálogo Institucional de CDT y Renta Fija con Curva Macro")
  st.info(
      f"📊 Tasa de Referencia Banrep Actual:"
      f" {st.session_state.macro_tasas_banrep*100:.2f}% E.A."
  )

  tab1, tab2 = st.tabs(["📌 CDT", "📜 Renta Fija (Bonos / TES)"])

  with tab1:
    busq_c = st.text_input("🔍 Buscar CDT por entidad:")
    for cdt in st.session_state.all_cdts:
      if (
          busq_c.strip() == ""
          or busq_c.upper() in cdt["entidad"].upper()
          or busq_c.upper() in cdt["id"].upper()
      ):
        st.markdown(
            f"""
                <div class="asset-card">
                    <h4>{cdt['id']} - {cdt['entidad']}</h4>
                    <p>{cdt['desc']}</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
        m_cdt = st.number_input(
            "Monto COP",
            50000,
            50000000,
            100000,
            step=50000,
            key=f"mc_{cdt['id']}",
        )
        if st.button(f"Invertir en CDT 🏦", key=f"bc_{cdt['id']}"):
          if u_data["cash"] >= m_cdt:
            u_data["cash"] -= m_cdt
            u_data["cdt_list"].append({"entidad": cdt["id"], "monto": m_cdt})
            save_user_to_db(usuario_activo, u_data)
            st.success("¡Invertido en CDT con éxito!")
            st.rerun()
          else:
            st.error("Efectivo insuficiente.")

  with tab2:
    busq_r = st.text_input("🔍 Buscar Renta Fija por emisor:")
    for rf in st.session_state.all_rf:
      if (
          busq_r.strip() == ""
          or busq_r.upper() in rf["emisor"].upper()
          or busq_r.upper() in rf["id"].upper()
      ):
        st.markdown(
            f"""
                <div class="asset-card">
                    <h4>{rf['id']} - {rf['emisor']}</h4>
                    <p>{rf['desc']}</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
        m_rf = st.number_input(
            "Monto COP",
            50000,
            50000000,
            100000,
            step=50000,
            key=f"mr_{rf['id']}",
        )
        if st.button(f"Comprar Renta Fija 📜", key=f"br_{rf['id']}"):
          if u_data["cash"] >= m_rf:
            u_data["cash"] -= m_rf
            u_data["renta_fija_list"].append({"tipo": rf["id"], "monto": m_rf})
            save_user_to_db(usuario_activo, u_data)
            st.success("¡Comprado Renta Fija con éxito!")
            st.rerun()
          else:
            st.error("Efectivo insuficiente.")

elif menu in [
    "🛒 8. Terminal Bursátil (Compra/Venta)",
    "🛒 7. Terminal Bursátil (Compra/Venta)",
]:
  st.title(
      "🛒 Terminal Bursátil de Compra y Venta (Exacta a la Bolsa de Valores)"
  )
  ticker_op = st.selectbox(
      "Seleccione Activo / Ticker:", list(st.session_state.prices.keys())
  )
  prc_op = st.session_state.prices[ticker_op]
  hist_op = st.session_state.history[ticker_op]
  bid_prc, ask_prc = int(prc_op * 0.998), int(prc_op * 1.002)

  c_info1, c_info2, c_info3 = st.columns(3)
  with c_info1:
    st.metric("Precio Último (Last)", f"${prc_op:,.0f} COP")
  with c_info2:
    st.metric("Punta de Compra (Bid)", f"${bid_prc:,.0f} COP")
  with c_info3:
    st.metric("Punta de Venta (Ask)", f"${ask_prc:,.0f} COP")

  fig_term = px.line(
      y=hist_op, labels={"x": "Rueda", "y": "Precio COP"}, title=f"Gráfico {ticker_op}"
  )
  fig_term.update_layout(
      margin=dict(l=10, r=10, t=30, b=10),
      height=180,
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font=dict(color="white"),
  )
  st.plotly_chart(fig_term, use_container_width=True)

  tab_compra, tab_venta = st.tabs(["🟢 Comprar Acciones", "🔴 Vender Acciones"])
  with tab_compra:
    cant_compra = st.number_input(
        "Cantidad a Comprar:", 1, 100000, 10, key="cc_val"
    )
    costo_total = ask_prc * cant_compra
    st.write(f"**Costo Total Estimado:** ${costo_total:,.0f} COP")
    if st.button("Ejecutar Orden de Compra ⚡", key="btn_ej_compra"):
      if u_data["cash"] >= costo_total:
        u_data["cash"] -= costo_total
        u_data["portfolio_acciones"][ticker_op] = (
            u_data["portfolio_acciones"].get(ticker_op, 0) + cant_compra
        )
        save_user_to_db(usuario_activo, u_data)
        st.success("¡Compra ejecutada con éxito!")
        st.rerun()
      else:
        st.error("Efectivo insuficiente.")

  with tab_venta:
    en_posesion = u_data["portfolio_acciones"].get(ticker_op, 0)
    st.info(f"Tienes actualmente **{en_posesion}** títulos.")
    if en_posesion > 0:
      cant_venta = st.number_input(
          "Cantidad a Vender:",
          1,
          en_posesion,
          min(1, en_posesion),
          key="cv_val",
      )
      recaudo_total = bid_prc * cant_venta
      if st.button("Ejecutar Orden de Venta ⚡", key="btn_ej_venta"):
        u_data["cash"] += recaudo_total
        u_data["portfolio_acciones"][ticker_op] -= cant_venta
        if u_data["portfolio_acciones"][ticker_op] <= 0:
          del u_data["portfolio_acciones"][ticker_op]
        save_user_to_db(usuario_activo, u_data)
        st.success("¡Venta ejecutada con éxito!")
        st.rerun()
    else:
      st.warning("No posees acciones para vender.")

elif menu == "🌱 9. Fondo ESG Sostenible":
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

elif menu in ["📰 10. Sala de Noticias Reales", "📰 10. Sala de Noticias"]:
  st.title("📰 Sala de Noticias Financieras (Globales y Nacionales)")
  st.write(
      "Boletines actualizados en tiempo real sobre la BVC, tasas del Banrep,"
      " petróleo Brent y mercados internacionales."
  )
  busc_n = st.text_input("🔍 Buscar noticia:")
  for fuente, txt in st.session_state.news_feed:
    if busc_n.strip() == "" or busc_n.upper() in txt.upper():
      st.markdown(
          f"""
            <div class="asset-card">
                <h4>{fuente}</h4>
                <p>{txt}</p>
            </div>
        """,
          unsafe_allow_html=True,
      )

elif menu == "📝 11. Tareas e Informe":
  st.title("📝 Módulo de Tareas y Justificación Analítica")
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
      if st.button("Enviar Tarea al Profesor 🚀", key=f"btn_{tit}"):
        info["entregas"][usuario_activo] = {
            "portafolio": u_data["portfolio_acciones"],
            "informe": informe,
        }
        save_assignment_to_db(tit, info)
        save_user_to_db(usuario_activo, u_data)
        st.success("¡Enviado correctamente!")
        st.rerun()

elif menu == "👨‍🏫 11. Panel de Asignaciones (Profesor)":
  st.title("👨‍🏫 Panel de Control Docente Avanzado")
  with st.form("form_p_panel"):
    t_tit = st.text_input("Título de Actividad:")
    t_desc = st.text_area("Descripción:")
    t_sem = st.selectbox(
        "Semestre Objetivo:", [f"Semestre {i}" for i in range(1, 11)]
    )
    t_pres = st.number_input(
        "Presupuesto Inicial (COP):", 500000, 50000000, 5000000, 500000
    )

    st.markdown("---")
    st.subheader("⚙️ Configuración de Múltiples Eventos de Decisión")
    sem_1 = st.number_input("Día / Semana Evento 1", value=5, min_value=1)
    tit_1 = st.text_input("Título Evento 1", value="SHOCK INFLACIONARIO")
    desc_1 = st.text_area("Descripción 1", value="El Banrep sube tasas.")
    oa_1 = st.text_input("Opción A (Evento 1)", value="Rebalancear a Renta Fija")
    ob_1 = st.text_input(
        "Opción B (Evento 1)", value="Mantener Renta Variable"
    )

    sem_2 = st.number_input("Día / Semana Evento 2", value=15, min_value=1)
    tit_2 = st.text_input("Título Evento 2", value="CRISIS PETROLERA")
    desc_2 = st.text_area("Descripción 2", value="Choque de oferta de crudo.")
    oa_2 = st.text_input("Opción A (Evento 2)", value="Tomar utilidades")
    ob_2 = st.text_input("Opción B (Evento 2)", value="Mantener posición")

    guardado = st.form_submit_button("Publicar Actividad con Eventos 🚀")
    if guardado and t_tit.strip():
      st.session_state.prof_assignments[t_tit] = {
          "descripcion": t_desc,
          "semestre_objetivo": t_sem,
          "presupuesto_inicial": t_pres,
          "eventos_claves": {
              int(sem_1): {
                  "tipo": "decision",
                  "titulo": tit_1,
                  "desc": desc_1,
                  "impacto": -1,
                  "op_a": oa_1,
                  "ef_a": "Protege el portafolio.",
                  "op_b": ob_1,
                  "ef_b": "Asume la volatilidad.",
              },
              int(sem_2): {
                  "tipo": "decision",
                  "titulo": tit_2,
                  "desc": desc_2,
                  "impacto": 1,
                  "op_a": oa_2,
                  "ef_a": "Asegura liquidez.",
                  "op_b": ob_2,
                  "ef_b": "Aprovecha el ciclo alcista.",
              },
          },
          "entregas": {},
      }
      save_assignment_to_db(t_tit, st.session_state.prof_assignments[t_tit])
      st.success(f"¡Actividad '{t_tit}' publicada con éxito!")

  st.markdown("---")
  for tit, dat in st.session_state.prof_assignments.items():
    st.markdown(
        f"**📌 {tit}** (Dirigida a {dat['semestre_objetivo']} | Presupuesto:"
        f" ${dat['presupuesto_inicial']:,.0f} COP)"
    )
    st.write(
        "Entregas de estudiantes:"
        f" **{len(dat['entregas'].keys())}** recibidas."
    )
    for est_n, entreg in dat["entregas"].items():
      with st.expander(f"🔍 Ver informe y portafolio de: {est_n}"):
        st.write(f"**Informe Analítico:** {entreg['informe']}")
        st.markdown("**Portafolio Acciones:**")
        st.json(entreg["portafolio"])
    st.markdown("---")

elif menu in [
    "⏳ 12. Simulación Monte Carlo & Plazo",
    "⏳ 9. Simulación Monte Carlo & Plazo",
]:
  st.title(
      "⏳ Simulador Estocástico Monte Carlo con Plazo de Inversión Personalizado"
  )
  unidad_tiempo = st.selectbox(
      "Unidad de Plazo de Inversión:", ["Días", "Semanas", "Meses", "Años"]
  )
  cantidad_plazo = st.number_input(
      "Cantidad del Plazo:", min_value=1, max_value=360, value=30
  )

  if unidad_tiempo == "Días":
    total_dias = cantidad_plazo
  elif unidad_tiempo == "Semanas":
    total_dias = cantidad_plazo * 7
  elif unidad_tiempo == "Meses":
    total_dias = cantidad_plazo * 30
  else:
    total_dias = cantidad_plazo * 365

  valor_inicial_acciones = sum(
      cant * st.session_state.prices[ticker]
      for ticker, cant in u_data["portfolio_acciones"].items()
      if cant > 0
  )

  if "sim_dias" not in st.session_state:
    st.session_state.sim_dias = 0
    st.session_state.sim_hist = []
    st.session_state.sim_running = False
    st.session_state.esperando_decision = False
    st.session_state.evento_activo_data = None

  c1, c2 = st.columns(2)
  with c1:
    if st.button("🚀 Iniciar Simulación Monte Carlo"):
      st.session_state.sim_dias = 1
      st.session_state.sim_hist = [
          valor_inicial_acciones if valor_inicial_acciones > 0 else 100000
      ]
      st.session_state.sim_running = True
      st.session_state.esperando_decision = False
      st.rerun()
  with c2:
    btn_avanzar = st.button(
        "⏭ Avanzar 1 Paso (Estocástico)",
        disabled=st.session_state.get("esperando_decision", False),
    )
    if st.session_state.sim_running and btn_avanzar:
      st.session_state.sim_dias += 1
      st.session_state.current_date += datetime.timedelta(days=1)

      for t_k in st.session_state.prices:
        var = random.normalvariate(0.0008, 0.018)
        new_prc = max(100, int(st.session_state.prices[t_k] * (1 + var)))
        st.session_state.prices[t_k] = new_prc
        st.session_state.history[t_k].append(new_prc)

      evento_activo_actual = None
      for t_key, t_val in st.session_state.prof_assignments.items():
        if (
            t_val["semestre_objetivo"] == u_data.get("semestre", "")
            and "eventos_claves" in t_val
        ):
          if st.session_state.sim_dias in t_val["eventos_claves"]:
            ev_data = t_val["eventos_claves"][st.session_state.sim_dias]
            evento_activo_actual = {
                "tipo": ev_data["tipo"],
                "titulo": ev_data["titulo"],
                "desc": ev_data["desc"],
                "impacto": ev_data["impacto"],
                "op_a": ev_data["op_a"],
                "ef_a": ev_data["ef_a"],
                "op_b": ev_data["op_b"],
                "ef_b": ev_data["ef_b"],
            }
            break

      st.session_state.evento_activo_data = evento_activo_actual

      if evento_activo_actual:
        st.session_state.esperando_decision = True
        st.rerun()
      else:
        v_acc_act = sum(
            cant * st.session_state.prices[ticker]
            for ticker, cant in u_data["portfolio_acciones"].items()
            if cant > 0
        )
        if v_acc_act == 0:
          v_acc_act = st.session_state.sim_hist[-1] * (
              1 + random.normalvariate(0.0005, 0.012)
          )
        st.session_state.sim_hist.append(v_acc_act)

        if st.session_state.sim_dias > total_dias:
          st.session_state.sim_running = False
          st.success("¡Simulación Monte Carlo completada con éxito!")
        st.rerun()

  if st.session_state.sim_running and st.session_state.sim_hist:
    st.subheader(
        f"📅 Progreso: Paso {st.session_state.sim_dias} de {total_dias}"
        f" ({cantidad_plazo} {unidad_tiempo}) | Fecha:"
        f" {st.session_state.current_date} | Valor Portafolio:"
        f" ${st.session_state.sim_hist[-1]:,.0f} COP".replace(",", ".")
    )

    if st.session_state.get("esperando_decision") and st.session_state.get(
        "evento_activo_data"
    ):
      ev = st.session_state.evento_activo_data
      st.error(
          f"🚨 **EVENTO CRÍTICO DE MERCADO (DECISIÓN OBLIGATORIA):"
          f" {ev['titulo']}**\n\n*{ev['desc']}*"
      )
      col_d1, col_d2 = st.columns(2)
      with col_d1:
        st.markdown(f"**{ev['op_a']}**")
        st.caption(f"📝 *Efectivo/Efecto:* {ev['ef_a']}")
        if st.button("Aplicar Opción A 🛡️", key="btn_op_a"):
          v_acc_act = (
              sum(
                  cant * st.session_state.prices[ticker]
                  for ticker, cant in u_data["portfolio_acciones"].items()
                  if cant > 0
              )
              * 1.03
          )
          st.session_state.sim_hist.append(v_acc_act)
          st.session_state.esperando_decision = False
          st.session_state.evento_activo_data = None
          st.success("¡Opción A aplicada!")
          st.rerun()
      with col_d2:
        st.markdown(f"**{ev['op_b']}**")
        st.caption(f"📝 *Efecto:* {ev['ef_b']}")
        if st.button("Aplicar Opción B 💎", key="btn_op_b"):
          v_acc_act = (
              sum(
                  cant * st.session_state.prices[ticker]
                  for ticker, cant in u_data["portfolio_acciones"].items()
                  if cant > 0
              )
              * 1.07
          )
          st.session_state.sim_hist.append(v_acc_act)
          st.session_state.esperando_decision = False
          st.session_state.evento_activo_data = None
          st.success("¡Opción B aplicada!")
          st.rerun()

    df_sim = pd.DataFrame(
        {
            "Paso": [f"Paso {i}" for i in range(len(st.session_state.sim_hist))],
            "Escenario Base COP": st.session_state.sim_hist,
            "Escenario Optimista (95%)": [
                val * (1 + 0.004 * i)
                for i, val in enumerate(st.session_state.sim_hist)
            ],
            "Escenario Pesimista (5%)": [
                val * (1 - 0.003 * i)
                for i, val in enumerate(st.session_state.sim_hist)
            ],
        }
    )
    fig_mc = px.line(
        df_sim,
        x="Paso",
        y=[
            "Escenario Base COP",
            "Escenario Optimista (95%)",
            "Escenario Pesimista (5%)",
        ],
        title="Simulación Estocástica de Monte Carlo (Bandas de Confianza)",
    )
    fig_mc.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )
    st.plotly_chart(fig_mc, use_container_width=True)

elif menu in ["🧠 13. Alertas de Riesgo & Correlación", "🧠 10. Alertas de Riesgo & Correlación"]:
  st.title("🧠 Módulo Novedoso: Alertas de Riesgo & Correlación de Portafolio")
  st.write(
      "Sistema inteligente que analiza automáticamente la concentración de tu"
      " portafolio, el riesgo sectorial y emite alertas preventivas ante"
      " choques macroeconómicos."
  )

  acc_poseidas = {
      k: v for k, v in u_data["portfolio_acciones"].items() if v > 0
  }
  if not acc_poseidas and not u_data["cdt_list"] and not u_data["renta_fija_list"]:
    st.warning(
        "⚠️ No tienes inversiones activas en este momento para auditar riesgo."
    )
  else:
    total_acc_val = sum(
        cant * st.session_state.prices[t] for t, cant in acc_poseidas.items()
    )
    total_cdt_val = sum(c["monto"] for c in u_data["cdt_list"])
    total_rf_val = sum(r["monto"] for r in u_data["renta_fija_list"])
    tot_pat = total_acc_val + total_cdt_val + total_rf_val + u_data["cash"]

    if tot_pat > 0:
      pct_acc = (total_acc_val / tot_pat) * 100
      pct_liq = (u_data["cash"] / tot_pat) * 100
      pct_rf = ((total_cdt_val + total_rf_val) / tot_pat) * 100

      col_r1, col_r2, col_r3 = st.columns(3)
      with col_r1:
        st.metric("Exposición Renta Variable", f"{pct_acc:.1f}%")
      with col_r2:
        st.metric("Exposición Renta Fija / CDT", f"{pct_rf:.1f}%")
      with col_r3:
        st.metric("Liquidez Disponible", f"{pct_liq:.1f}%")

      st.markdown("---")
      st.subheader("🚨 Diagnóstico de Riesgo Institucional")
      if pct_acc > 70:
        st.error(
            "🔴 **ALERTA ROJA DE CONCENTRACIÓN:** Tu portafolio está altamente"
            " expuesto a renta variable (>70%). Ante un shock de tasas del"
            " Banrep o caída del petróleo, tu patrimonio sufrirá alta"
            " volatilidad. Se recomienda diversificar hacia CDT o TES."
        )
      elif pct_rf > 70:
        st.warning(
            "🟡 **ALERTA AMARILLA DE COSTO DE OPORTUNIDAD:** Tienes más del 70%"
            " en renta fija. Estás perdiendo el rally alcista de acciones con"
            " alto potencial de crecimiento."
        )
      else:
        st.success(
            "🟢 **PORTAFOLIO SALUDABLE Y EQUILIBRADO:** Mantienes una proporción"
            " óptima entre liquidez, renta variable y renta fija. ¡Excelente"
            " gestión gerencial!"
        )

      fig_pie = px.pie(
          names=["Acciones", "CDT & Renta Fija", "Efectivo Libre"],
          values=[total_acc_val, total_cdt_val + total_rf_val, u_data["cash"]],
          title="Distribución de Riesgo por Clase de Activo",
      )
      fig_pie.update_layout(
          height=350,
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          font=dict(color="white"),
      )
      st.plotly_chart(fig_pie, use_container_width=True)