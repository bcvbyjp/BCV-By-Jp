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
# ESTILOS CSS CON EFECTOS NEÓN + GLASSMORPHISM + HOVER INTERACTIVO
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

    /* Hero de Masterclass Jp en Pantalla Gigante con Luz Neón Intensa */
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

    /* Tarjetas Interactivas con Neón Azul / Cyan y Animación Hover */
    .neon-card {
        background: linear-gradient(135deg, rgba(16, 22, 34, 0.85) 0%, rgba(26, 34, 51, 0.85) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(88, 166, 255, 0.35);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5), 0 0 15px rgba(56, 189, 248, 0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .neon-card:hover {
        transform: translateY(-7px);
        border-color: #38bdf8;
        box-shadow: 0 15px 35px rgba(56, 189, 248, 0.35), 0 0 25px rgba(56, 189, 248, 0.25);
    }

    /* Tarjetas Especiales Verde Neón (Motivación / Interés Compuesto) */
    .neon-card-green {
        background: linear-gradient(135deg, rgba(6, 32, 18, 0.85) 0%, rgba(13, 48, 26, 0.85) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(46, 160, 67, 0.5);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5), 0 0 20px rgba(46, 160, 67, 0.2);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .neon-card-green:hover {
        transform: translateY(-7px);
        border-color: #2ea043;
        box-shadow: 0 15px 35px rgba(46, 160, 67, 0.45), 0 0 30px rgba(46, 160, 67, 0.3);
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
# BANNER GLOBAL DE JP EN LA PARTE SUPERIOR
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
        ["Masterclass BVC con Jp", "Terminal Bursátil", "Catálogo Técnico", "CDT y Bonos", "Fondo ESG"],
        icons=["camera-reels", "cart", "graph-up", "bank", "tree"],
        menu_icon="compass", default_index=0
    )

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

render_guia_banner_global()

# ==========================================
# MASTERCLASS DE JP CON LUZ NEÓN + HOVER INTERACTIVO
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

    # HERO GIGANTE
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