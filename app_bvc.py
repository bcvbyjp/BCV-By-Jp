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
# ESTILOS CSS (PANTALLA GIGANTE JP + GLASSMORPHISM)
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

    /* Banner Global de Jp en la parte superior */
    .jp-global-banner {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%);
        border: 2px solid #facc15;
        border-radius: 20px;
        padding: 16px 22px;
        margin-bottom: 25px;
        box-shadow: 0 0 25px rgba(250, 204, 21, 0.2);
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .jp-avatar-img {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #facc15;
        box-shadow: 0 0 15px rgba(250, 204, 21, 0.5);
        animation: floatJp 3.5s ease-in-out infinite;
    }

    /* Pantalla Gigante / Hero de Masterclass Jp */
    .hero-jp-masterclass {
        background: radial-gradient(circle at top center, #1e293b 0%, #0f172a 100%);
        border: 2px solid #facc15;
        border-radius: 28px;
        padding: 40px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 45px rgba(250, 204, 21, 0.25);
    }

    .jp-masterclass-img {
        width: 170px;
        height: 170px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #facc15;
        box-shadow: 0 0 30px rgba(250, 204, 21, 0.6);
        margin-bottom: 15px;
        animation: floatJp 3.5s ease-in-out infinite;
    }

    @keyframes floatJp {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-6px) scale(1.02); }
        100% { transform: translateY(0px) scale(1); }
    }

    .asset-card {
        background: linear-gradient(135deg, #101622 0%, #1a2233 100%);
        border: 1px solid rgba(31, 111, 235, 0.4);
        border-radius: 20px;
        padding: 26px;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .asset-card:hover {
        border-color: #58a6ff;
        box-shadow: 0 12px 30px rgba(88, 166, 255, 0.25);
    }

    .concept-badge {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
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
# BANNER GLOBAL DE JP (PARTE SUPERIOR)
# ==========================================
def render_guia_banner_global():
    has_img = os.path.exists("jp_foto.jpg")
    img_html = ""
    if has_img:
        with open("jp_foto.jpg", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_html = f'<img src="data:image/jpeg;base64,{img_b64}" class="jp-avatar-img" />'
    else:
        img_html = '<div style="font-size: 3.5rem;">👨‍‍💼</div>'

    st.markdown(
        f"""
        <div class="jp-global-banner">
            <div>{img_html}</div>
            <div style="flex-grow: 1;">
                <h3 style="color: #facc15; margin: 0; font-size: 1.35rem;">🟡 Jp - Tu Guía Virtual Unisucre</h3>
                <p style="color: #e2e8f0; margin: 4px 0 0 0; font-size: 0.95rem;">
                    ¡Epa, <b>{usuario_activo}</b>! Estás en la plataforma oficial de simulación bursátil de Unisucre. Revisa la <b>Masterclass de Jp</b> para aprender la teoría antes de hacer tu primera operación.
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
        ["Masterclass BVC con Jp", "Terminal Bursátil", "Catálogo Técnico", "CDT y Bonos", "Fondo ESG"],
        icons=["camera-reels", "cart", "graph-up", "bank", "tree"],
        menu_icon="compass", default_index=0
    )

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

# RENDERIZAR BANNER GLOBAL EN TODAS LAS VISTAS
render_guia_banner_global()

# ==========================================
# MÓDULO: MASTERCLASS PANTALLA GIGANTE CON JP
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

    # PANTALLA GIGANTE / HERO
    st.markdown(
        f"""
        <div class="hero-jp-masterclass">
            {img_hero_html}
            <h1 style="color: #facc15; font-size: 2.5rem; margin-bottom: 8px;">🎓 Masterclass de Bolsa de Valores de Colombia (BVC)</h1>
            <h3 style="color: #94a3b8; font-weight: 400; margin-bottom: 20px; font-size: 1.2rem;">
                Dictado por <b>Juan Pablo López Tarriba (Jp)</b> | Universidad de Sucre
            </h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; max-width: 850px; margin: 0 auto; line-height: 1.7;">
                ¡Habla, equipo! Si nunca has escuchado sobre acciones, dividendos, tasas de interés o gráficos bursátiles, <b>¡tranquilo, estás en el lugar correcto!</b> 
                Esta guía interactiva fue pensada para que pases de cero a entender exactamente cómo funciona el mercado de capitales colombiano y administres con cabeza tu bono inicial de <b>$500.000 COP</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # NUCLEO EDUCATIVO EN PROFUNDIDAD
    st.markdown("## 📚 Módulos Fundamentales de Formación Financiera")

    tab_m1, tab_m2, tab_m3, tab_m4 = st.tabs([
        "🏛️ 1. ¿Qué es la BVC y su Rol?",
        "⚖️ 2. Renta Variable vs. Renta Fija",
        "📊 3. El Índice COLCAP y Activos",
        "🧠 4. Psicología y Gestión del Riesgo"
    ])

    with tab_m1:
        st.markdown(
            """
            <div class="asset-card">
                <span class="concept-badge">Fundamentos Institucionales</span>
                <h2 style="margin-top: 10px;">🏛️ La Bolsa de Valores de Colombia (BVC)</h2>
                <p style="font-size: 1.05rem; line-height: 1.8;">
                    La <b>Bolsa de Valores de Colombia (BVC)</b> es una entidad privada encargada de administrar los mercados de acciones, bonos, divisas y derivados en nuestro país. 
                    Funciona como la gran plaza de mercado oficial donde las empresas colombianas consiguen dinero para construir carreteras, expansionar fábricas o lanzar productos, y donde los inversionistas (como tú) ponen a rentar su capital.
                </p>
                <hr style="border-color: rgba(255,255,255,0.1);">
                <h3>🛡️ Entidades que Vigilan y Protegen el Mercado:</h3>
                <ul>
                    <li><b>Superintendencia Financiera de Colombia (SFC):</b> Inspecciona y vigila que todas las operaciones de la bolsa cumplan la ley y protejan al inversionista.</li>
                    <li><b>Autoregulador del Mercado de Valores (AMV):</b> Vela por la ética y la transparencia de los corredores y traders profesionales.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

    with tab_m2:
        col_rv, col_rf = st.columns(2)
        with col_rv:
            st.markdown(
                """
                <div class="asset-card" style="min-height: 380px;">
                    <span class="concept-badge">Mayor Riesgo / Mayor Retorno</span>
                    <h2 style="margin-top: 10px;">📈 Renta Variable (Acciones)</h2>
                    <p style="font-size: 1rem; line-height: 1.7;">
                        Cuando compras una acción (ej. <b>Ecopetrol</b> o <b>Bancolombia</b>), te conviertes en <b>socio copropietario</b> directo de esa empresa en proporción a tus títulos.
                    </p>
                    <h4 style="color: #2ea043;">¿Cómo ganas dinero aquí?</h4>
                    <ol>
                        <li><b>Valorización del Precio:</b> Compras la acción a $2.500 COP y sube a $3.000 COP gracias al crecimiento de la empresa.</li>
                        <li><b>Dividendos:</b> La asamblea de accionistas reparte periódicamente las ganancias generadas a todos los dueños.</li>
                    </ol>
                    <p style="color: #f87171; font-size: 0.9rem;">⚠️ <i>El precio puede subir o bajar diariamente según la oferta, la demanda y las noticias económicas.</i></p>
                </div>
                """, unsafe_allow_html=True
            )
        with col_rf:
            st.markdown(
                """
                <div class="asset-card" style="min-height: 380px;">
                    <span class="concept-badge">Seguridad y Previsibilidad</span>
                    <h2 style="margin-top: 10px;">📜 Renta Fija (TES y CDT)</h2>
                    <p style="font-size: 1rem; line-height: 1.7;">
                        Aquí no te conviertes en socio, sino en <b>prestamista</b>. Le prestas tu dinero al Estado Colombiano (mediante Títulos TES) o a Bancos (CDT).
                    </p>
                    <h4 style="color: #2ea043;">¿Cómo ganas dinero aquí?</h4>
                    <ol>
                        <li><b>Tasa de Interés Conocida:</b> Desde el día 1 acuerdas pactar una tasa fija (ej. 11.5% Efectivo Anual).</li>
                        <li><b>Preservación de Capital:</b> El riesgo de impago es extremadamente bajo porque está respaldado por la Nación o Fogafin.</li>
                    </ol>
                    <p style="color: #38bdf8; font-size: 0.9rem;">💡 <i>Ideal para proteger tu capital contra la inflación y mantener saldo seguro.</i></p>
                </div>
                """, unsafe_allow_html=True
            )

    with tab_m3:
        st.markdown(
            """
            <div class="asset-card">
                <span class="concept-badge">Indicador Clave</span>
                <h2 style="margin-top: 10px;">🇨🇴 El Índice MSCI COLCAP</h2>
                <p style="font-size: 1.05rem; line-height: 1.8;">
                    Es el <b>termómetro de la economía colombiana</b>. El COLCAP agrupa las <b>20 acciones más líquidas e importantes</b> del mercado local. 
                    Si el índice COLCAP sube en el día, significa que en general las grandes empresas del país están ganando valor y confianza.
                </p>
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown("### 🏢 Activos Colombianos Emblemáticos en tu Terminal")
        df_empresas = pd.DataFrame([
            {"Ticker": "ECOPETROL", "Sector": "Petróleo y Gas", "Importancia en Colombia": "La empresa más grande del país. Representa gran parte de los ingresos fiscales del Estado."},
            {"Ticker": "BCOLOMBIA", "Sector": "Banca / Financiero", "Importancia en Colombia": "El banco líder en activos y clientes. Mide directamente la salud del consumo de las familias."},
            {"Ticker": "ISA", "Sector": "Infraestructura Eléctrica", "Importancia en Colombia": "Transporta la mayor parte de la energía de Colombia y Latinoamérica con contratos a muy largo plazo."},
            {"Ticker": "GRUPOSURA", "Sector": "Holding Financiero", "Importancia en Colombia": "Conglomerado dueño de fondos de pensiones, seguros y participaciones bancarias regionales."}
        ])
        st.table(df_empresas)

    with tab_m4:
        st.markdown(
            """
            <div class="asset-card">
                <span class="concept-badge">Mente de Trader Exitoso</span>
                <h2 style="margin-top: 10px;">🧠 Psicología Bursátil y Gestión de Riesgo por Jp</h2>
                <p style="font-size: 1.05rem; line-height: 1.8;">
                    En los mercados financieros, el mayor enemigo no es el gráfico ni las noticias, <b>¡es la falta de disciplina!</b> 
                    Para conservar tus $500.000 COP e ir escalando en el Ranking de la Universidad de Sucre, aplica las 3 reglas de oro de Jp:
                </p>
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 20px;">
                    <div style="flex: 1; min-width: 240px; background: rgba(15, 23, 42, 0.8); padding: 18px; border-radius: 16px; border: 1px solid rgba(250,204,21,0.3);">
                        <h4 style="color: #facc15;">1. Diversificación Inteligente</h4>
                        <p style="font-size: 0.95rem;">Nunca gastes el 100% de tu dinero en un solo activo. Divide tu capital entre acciones, CDT y efectivo libre.</p>
                    </div>
                    <div style="flex: 1; min-width: 240px; background: rgba(15, 23, 42, 0.8); padding: 18px; border-radius: 16px; border: 1px solid rgba(56,189,248,0.3);">
                        <h4 style="color: #38bdf8;">2. Control de Emociones</h4>
                        <p style="font-size: 0.95rem;">No compres desesperado cuando los precios estén en máximos, ni vendas con pánico cuando haya caídas temporales.</p>
                    </div>
                    <div style="flex: 1; min-width: 240px; background: rgba(15, 23, 42, 0.8); padding: 18px; border-radius: 16px; border: 1px solid rgba(46,160,67,0.3);">
                        <h4 style="color: #2ea043;">3. Monitoreo Constante</h4>
                        <p style="font-size: 0.95rem;">Revisa las alertas de riesgo y analiza los indicadores técnicos (SMA / RSI) antes de tomar una decisión.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

elif menu == "Terminal Bursátil":
    st.title("🛒 Terminal Bursátil de Compra y Venta")
    st.success("Aplica los conocimientos de la Masterclass e invierte tus $500,000 COP.")

elif menu == "Catálogo Técnico":
    st.title("📊 Catálogo Técnico de Activos")
    st.info("Revisa las tendencias de precios en tiempo real.")

elif menu == "CDT y Bonos":
    st.title("🏦 Renta Fija: CDT y Bonos Soberanos")
    st.info("Asegura tasas fijas con riesgo mínimo.")

elif menu == "Fondo ESG":
    st.title("🌱 Fondo Sostenible ESG")
    st.info("Invierta en empresas con alto impacto ambiental y social.")