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
# ESTILOS CSS (FINTECH PREMIUM CORREGIDO)
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

    /* Hero Masterclass */
    .hero-jp-masterclass {
        background: radial-gradient(circle at top center, #1e293b 0%, #0f172a 100%);
        border: 2px solid #facc15;
        border-radius: 28px;
        padding: 40px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 40px rgba(250, 204, 21, 0.2);
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

    .info-card {
        background: linear-gradient(135deg, #101622 0%, #1a2233 100%);
        border: 1px solid rgba(31, 111, 235, 0.35);
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 15px;
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
                <h3 style="color: #facc15; margin: 0; font-size: 1.35rem;">🟡 Jp - Tu Guía Virtual Unisucre</h3>
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
        ["Masterclass BVC con Jp", "Terminal Bursátil", "Catálogo Técnico", "CDT y Bonos", "Fondo ESG"],
        icons=["camera-reels", "cart", "graph-up", "bank", "tree"],
        menu_icon="compass", default_index=0
    )

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

render_guia_banner_global()

# ==========================================
# MASTERCLASS CORREGIDA Y LIMPIA
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
            <h1 style="color: #facc15; font-size: 2.5rem; margin-bottom: 8px;">🎓 Masterclass de Inversión y Bolsa de Valores (BVC)</h1>
            <h3 style="color: #94a3b8; font-weight: 400; margin-bottom: 15px; font-size: 1.2rem;">
                Dictado por <b>Juan Pablo López Tarriba (Jp)</b> | Universidad de Sucre
            </h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; max-width: 850px; margin: 0 auto; line-height: 1.7;">
                ¡Habla, cuadro! Esta guía está hecha para romper el mito de que <i>"la bolsa es solo para ricos"</i> y darte las herramientas reales para administrar con inteligencia tu saldo inicial de <b>$500.000 COP</b>.
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
        st.subheader("🔥 ¿Por qué Invertir no es Opcional?")
        st.write(
            "Mucha gente cree que ahorrar dinero en una cuenta tradicional o debajo del colchón es seguro. "
            "**¡Gran error!** Existe un enemigo silencioso llamado **INFLACIÓN**. "
            "Si la inflación en Colombia es del 7% anual y tu dinero guardado te da el 1%, en realidad **estás perdiendo un 6% de poder de compra cada año**."
        )
        st.info(
            "✨ **El Secreto del Interés Compuesto:**\n\n"
            "Albert Einstein decía que el interés compuesto es la fuerza más poderosa del universo. Consiste en reinvertir las ganancias generadas para que tus intereses generen más intereses. "
            "Si inviertes $500.000 COP hoy con un retorno promedio del 12% anual y reinviertes tus ganancias, ¡tu dinero trabajará para ti de forma exponencial!"
        )

    with tab_m2:
        st.subheader("🏛️ ¿Qué es la BVC y cuál es su Rol en Colombia?")
        st.write(
            "La **Bolsa de Valores de Colombia (BVC)** es la plaza de mercado oficial donde se conectan las empresas que necesitan capital para crecer con las personas e instituciones que tienen ahorros disponibles."
        )
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(
                """
                <div class="info-card">
                    <h4>🏢 Empresas (Deficitarios)</h4>
                    <p>Emiten acciones o bonos para construir infraestructura, expandir plantas y crear empleo sin endeudarse únicamente con bancos.</p>
                </div>
                """, unsafe_allow_html=True
            )
        with col_c2:
            st.markdown(
                """
                <div class="info-card">
                    <h4>💼 Inversionistas (Superavitarios)</h4>
                    <p>Aportan capital a proyectos productivos a cambio de rentabilidades superiores a las de los métodos de ahorro tradicionales.</p>
                </div>
                """, unsafe_allow_html=True
            )
        st.success("🛡️ **Seguridad Garantizada:** El mercado está vigilado por la Superintendencia Financiera de Colombia (SFC) y el Autoregulador del Mercado de Valores (AMV).")

    with tab_m3:
        col_rv, col_rf = st.columns(2)
        with col_rv:
            st.markdown(
                """
                <div class="info-card">
                    <h3 style="color: #58a6ff;">📈 Renta Variable (Acciones)</h3>
                    <p>Te convierte en <b>socio copropietario</b> de empresas como Ecopetrol o Bancolombia.</p>
                    <ul>
                        <li><b>Valorización:</b> La acción sube de precio si la empresa crece.</li>
                        <li><b>Dividendos:</b> Reparto periódico de utilidades generadas.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True
            )
        with col_rf:
            st.markdown(
                """
                <div class="info-card">
                    <h3 style="color: #2ea043;">📜 Renta Fija (TES y CDT)</h3>
                    <p>Te convierte en <b>prestamista</b> del Estado o instituciones bancarias.</p>
                    <ul>
                        <li><b>Intereses Conocidos:</b> Tasa pactada desde el primer día (ej. 11.5% E.A.).</li>
                        <li><b>Riesgo Mínimo:</b> Respaldados por la Nación o el seguro FOGAFIN.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True
            )

    with tab_m4:
        st.subheader("🌎 Casos Reales: Lo que nos Enseña la Historia")
        st.markdown(
            """
            <div class="info-card">
                <h4 style="color: #facc15;">🌟 Caso 1: Anne Scheiber (El Poder de la Disciplina)</h4>
                <p>Anne era una auditora estadounidense con un salario modesto. Durante más de 50 años invirtió disciplinadamente pequeñas sumas en acciones de empresas sólidas y nunca vendió en pánico. Transformó unos miles de dólares en un patrimonio de <b>más de $22 millones de dólares</b>.</p>
            </div>
            <div class="info-card">
                <h4 style="color: #58a6ff;">🇨🇴 Caso 2: Dividendos en Colombia (Ecopetrol y Bancolombia)</h4>
                <p>Inversionistas en Colombia que compraron acciones de Ecopetrol o Bancolombia durante momentos de crisis y mantuvieron sus posiciones, han recibido <b>retornos anuales en dividendos del 10% al 15% sobre su inversión inicial</b>.</p>
            </div>
            """, unsafe_allow_html=True
        )

    with tab_m5:
        st.subheader("🧠 Las 4 Reglas de Oro de Jp")
        c1, c2 = st.columns(2)
        with c1:
            st.warning("1. **Nunca Inviertas a Ciegas:** Conoce el activo y la empresa antes de comprar.")
            st.info("2. **Diversifica:** Combina acciones de varios sectores con instrumentos de renta fija.")
        with c2:
            st.error("3. **Controla las Emociones:** No compres por euforia ni vendas con pánico.")
            st.success("4. **Visión a Largo Plazo:** La riqueza real se genera con constancia e interés compuesto.")

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