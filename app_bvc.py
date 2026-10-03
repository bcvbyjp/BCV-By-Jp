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
# ESTILOS CSS (PANTALLA GIGANTE JP + FINTECH PREMIUM)
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

    /* Hero de Masterclass Jp en Pantalla Gigante */
    .hero-jp-masterclass {
        background: radial-gradient(circle at top center, #1e293b 0%, #0f172a 100%);
        border: 2px solid #facc15;
        border-radius: 28px;
        padding: 45px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 50px rgba(250, 204, 21, 0.25);
    }

    .jp-masterclass-img {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #facc15;
        box-shadow: 0 0 35px rgba(250, 204, 21, 0.6);
        margin-bottom: 18px;
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
        padding: 28px;
        margin-bottom: 24px;
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
        padding: 5px 14px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .motive-box {
        background: rgba(35, 134, 54, 0.15);
        border: 1px solid rgba(46, 160, 67, 0.5);
        border-radius: 18px;
        padding: 20px;
        margin: 15px 0;
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
        img_html = '<div style="font-size: 3.5rem;">👨‍💼</div>'

    st.markdown(
        f"""
        <div class="jp-global-banner">
            <div>{img_html}</div>
            <div style="flex-grow: 1;">
                <h3 style="color: #facc15; margin: 0; font-size: 1.35rem;">🟡 Jp - Tu Guía Virtual Unisucre</h3>
                <p style="color: #e2e8f0; margin: 4px 0 0 0; font-size: 0.95rem;">
                    ¡Epa, <b>{usuario_activo}</b>! Bienvenido a la plataforma. Lee detenidamente la <b>Masterclass de Jp</b> para aprender por qué invertir no es un lujo, sino una necesidad para tu futuro profesional.
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
# MÓDULO: MASTERCLASS COMPLETA Y ENRIQUECIDA CON JP
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

    # HERO PANTALLA GIGANTE
    st.markdown(
        f"""
        <div class="hero-jp-masterclass">
            {img_hero_html}
            <h1 style="color: #facc15; font-size: 2.6rem; margin-bottom: 8px;">🎓 Masterclass de Inversión y Bolsa de Valores (BVC)</h1>
            <h3 style="color: #94a3b8; font-weight: 400; margin-bottom: 20px; font-size: 1.25rem;">
                Dictado por <b>Juan Pablo López Tarriba (Jp)</b> | Universidad de Sucre
            </h3>
            <p style="font-size: 1.15rem; color: #cbd5e1; max-width: 900px; margin: 0 auto; line-height: 1.8;">
                ¡Habla, cuadro! Si estás aquí es porque no quieres conformarte con dejar el dinero 'guardado bajo el colchón' viendo cómo pierde valor todos los días. 
                Esta Masterclass está diseñada para romper el mito de que <i>"la bolsa es solo para millonarios"</i> y darte el conocimiento técnico, las herramientas reales y la confianza para tomar el control de tu futuro financiero desde hoy mismo.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # NÚCLEO EDUCATIVO EN PROFUNDIDAD
    st.markdown("## 🚀 Módulos Magistrales de Formación Bursátil")

    tab_m1, tab_m2, tab_m3, tab_m4, tab_m5 = st.tabs([
        "💡 1. ¿Por qué Invertir? (El Poder del Capital)",
        "🏛️️ 2. ¿Qué es la BVC y cómo Funciona?",
        "⚖️ 3. Renta Variable vs. Renta Fija",
        "🌎 4. Casos Reales de Éxito y Lecciones",
        "🧠 5. Mente de Inversionista y Reglas de Oro"
    ])

    with tab_m1:
        st.markdown(
            """
            <div class="asset-card">
                <span class="concept-badge">El Despertar Financiero</span>
                <h2 style="margin-top: 10px;">🔥 ¿Por qué Invertir no es Opcional?</h2>
                <p style="font-size: 1.05rem; line-height: 1.8;">
                    Mucha gente cree que ahorrar dinero en una cuenta de ahorros tradicional o debajo del colchón es seguro. <b>¡Gran error!</b> 
                    Hay un enemigo silencioso llamado <b>INFLACIÓN</b>. La inflación es el aumento sostenido en los precios de las cosas (el pan, la gasolina, la matrícula universitaria). 
                    Si la inflación en Colombia es del 7% anual y tu dinero guardado en el banco te da el 1%, en realidad <b>estás perdiendo un 6% de poder de compra cada año</b>.
                </p>

                <div class="motive-box">
                    <h3 style="color: #2ea043; margin-top: 0;">✨ El Secreto del Interés Compuesto (La 8ª Maravilla del Mundo)</h3>
                    <p style="font-size: 1rem; line-height: 1.7; color: #e2e8f0;">
                        Albert Einstein decía que el interés compuesto es la fuerza más poderosa del universo. Consiste en reinvertir las ganancias generadas para que tus intereses generen más intereses. 
                        <b>Ejemplo práctico:</b> Si inviertes $500.000 COP hoy con un retorno promedio del 12% anual y reinviertes tus ganancias, en lugar de crecer en línea recta, tu capital despega de forma exponencial con el paso del tiempo. ¡El dinero trabaja para ti mientras duermes!
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

    with tab_m2:
        st.markdown(
            """
            <div class="asset-card">
                <span class="concept-badge">Mecanismo del Mercado</span>
                <h2 style="margin-top: 10px;">🏛️ ¿Qué es la BVC y cuál es su Rol en Colombia?</h2>
                <p style="font-size: 1.05rem; line-height: 1.8;">
                    La <b>Bolsa de Valores de Colombia (BVC)</b> es la infraestructura tecnológica y legal donde se encuentran dos tipos de personas:
                </p>
                <ol style="font-size: 1.05rem; line-height: 1.8;">
                    <li><b>Los Deficitarios (Empresas y Estado):</b> Necesitan dinero para construir infraestructura, expandir plantas o crear nuevos empleos. En lugar de pedirle todo a un banco, emiten acciones o bonos.</li>
                    <li><b>Los Superavitarios (Inversionistas):</b> Personas e instituciones con capital libre que buscan colocar su dinero en proyectos productivos para obtener una rentabilidad superior.</li>
                </ol>
                <hr style="border-color: rgba(255,255,255,0.1);">
                <h3>🛡️ ¿Es Seguro Invertir en la BVC?</h3>
                <p style="font-size: 1rem; line-height: 1.7;">
                    <b>¡Totalmente transparente!</b> El mercado de valores colombiano está rigurosamente regulado por la <b>Superintendencia Financiera de Colombia (SFC)</b> y auditado por el <b>Autoregulador del Mercado de Valores (AMV)</b>. Nadie puede 'desaparecer' con tu dinero porque los títulos quedan registrados en el Depósito Centralizado de Valores (DECEVAL).
                </p>
            </div>
            """, unsafe_allow_html=True
        )

    with tab_m3:
        col_rv, col_rf = st.columns(2)
        with col_rv:
            st.markdown(
                """
                <div class="asset-card" style="min-height: 420px;">
                    <span class="concept-badge">Crecimiento / Mayor Retorno</span>
                    <h2 style="margin-top: 10px;">📈 Renta Variable (Acciones)</h2>
                    <p style="font-size: 1rem; line-height: 1.7;">
                        Te convierte en <b>socio copropietario real</b> de grandes compañías como Ecopetrol, Bancolombia o ISA.
                    </p>
                    <h4 style="color: #2ea043;">¿Cómo generas ganancias?</h4>
                    <ul>
                        <li><b>Valorización del precio:</b> Si la empresa factura más y se expande, la acción sube de valor en el mercado secundario.</li>
                        <li><b>Dividendos:</b> Reparto de utilidades en efectivo que las empresas pagan directamente a los accionistas.</li>
                    </ul>
                    <p style="color: #f87171; font-size: 0.9rem;">⚠️ <i>Requiere paciencia y tolerancia a la volatilidad a corto plazo.</i></p>
                </div>
                """, unsafe_allow_html=True
            )
        with col_rf:
            st.markdown(
                """
                <div class="asset-card" style="min-height: 420px;">
                    <span class="concept-badge">Estabilidad y Protección</span>
                    <h2 style="margin-top: 10px;">📜 Renta Fija (TES y CDT)</h2>
                    <p style="font-size: 1rem; line-height: 1.7;">
                        Te convierte en <b>acreedor (prestamista)</b> del Estado Colombiano o de bancos de primer nivel.
                    </p>
                    <h4 style="color: #2ea043;">¿Cómo generas ganancias?</h4>
                    <ul>
                        <li><b>Cupones e Intereses:</b> Conoces exactamente la tasa pactada (ej. 11.5% E.A.) y la fecha exacta en la que recibirás tu capital más rendimientos.</li>
                        <li><b>Riesgo Mínimo:</b> Tienen respaldo del estado o seguro de depósito FOGAFIN.</li>
                    </ul>
                    <p style="color: #38bdf8; font-size: 0.9rem;">💡 <i>Ideal para armar la base sólida de tu portafolio.</i></p>
                </div>
                """, unsafe_allow_html=True
            )

    with tab_m4:
        st.markdown(
            """
            <div class="asset-card">
                <span class="concept-badge">Aprendizaje con Historia</span>
                <h2 style="margin-top: 10px;">🌎 Casos Reales: Lo que Nos Enseña la Historia</h2>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #facc15;">🌟 Caso 1: Anne Scheiber (El Poder de la Disciplina)</h3>
                    <p style="font-size: 1rem; line-height: 1.7;">
                        Anne era una auditora del gobierno estadounidense con un salario modesto. Nunca ganó un sueldo astronómico, pero durante más de 50 años invirtió disciplinadamente pequeñas sumas de dinero en acciones de empresas sólidas (como Coca-Cola y Pfizer) y nunca vendió en momentos de pánico. 
                        <b>¿El resultado?</b> Transformó unos pocos miles de dólares en un patrimonio de <b>más de $22 millones de dólares</b>.
                    </p>
                </div>

                <div>
                    <h3 style="color: #58a6ff;">🇨🇴 Caso 2: El Histórico Pagador de Dividendos en Colombia (Ecopetrol y Bancolombia)</h3>
                    <p style="font-size: 1rem; line-height: 1.7;">
                        En Colombia, inversionistas que compraron acciones de Ecopetrol o Bancolombia a precios desvalorizados durante crisis globales y mantuvieron sus posiciones, han recibido durante años retornos en <b>dividendos de hasta el 10% - 15% anual sobre su compra inicial</b>, superando con creces cualquier cuenta de ahorros tradicional.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

    with tab_m5:
        st.markdown(
            """
            <div class="asset-card">
                <span class="concept-badge">Mentalidad Unisucre</span>
                <h2 style="margin-top: 10px;">🧠 Las 4 Reglas de Oro de Jp para Operar con Éxito</h2>
                <p style="font-size: 1.05rem; line-height: 1.8;">
                    Para triunfar en este simulador y en la vida real, grábate estas reglas antes de tocar tus $500.000 COP iniciales:
                </p>
                <div style="display: flex; gap: 18px; flex-wrap: wrap; margin-top: 20px;">
                    <div style="flex: 1; min-width: 220px; background: rgba(15, 23, 42, 0.8); padding: 20px; border-radius: 16px; border: 1px solid rgba(250,204,21,0.4);">
                        <h4 style="color: #facc15; margin-top: 0;">1. Nunca Inviertas a Ciegas</h4>
                        <p style="font-size: 0.95rem; color: #cbd5e1;">Aprende sobre la empresa o activo antes de comprar. Revisa sus fundamentales y estados de resultados.</p>
                    </div>
                    <div style="flex: 1; min-width: 220px; background: rgba(15, 23, 42, 0.8); padding: 20px; border-radius: 16px; border: 1px solid rgba(56,189,248,0.4);">
                        <h4 style="color: #38bdf8; margin-top: 0;">2. Diversifica sin Miedo</h4>
                        <p style="font-size: 0.95rem; color: #cbd5e1;">Combina acciones de varios sectores (energía, bancos, tecnología) con instrumentos de renta fija.</p>
                    </div>
                    <div style="flex: 1; min-width: 220px; background: rgba(15, 23, 42, 0.8); padding: 20px; border-radius: 16px; border: 1px solid rgba(46,160,67,0.4);">
                        <h4 style="color: #2ea043; margin-top: 0;">3. Controla las Emociones</h4>
                        <p style="font-size: 0.95rem; color: #cbd5e1;">El mercado oscila todos los días. Mantén la calma en las caídas y no compres por euforia en los picos.</p>
                    </div>
                    <div style="flex: 1; min-width: 220px; background: rgba(15, 23, 42, 0.8); padding: 20px; border-radius: 16px; border: 1px solid rgba(168,85,247,0.4);">
                        <h4 style="color: #c084fc; margin-top: 0;">4. Visión a Largo Plazo</h4>
                        <p style="font-size: 0.95rem; color: #cbd5e1;">La riqueza verdadera en la bolsa se construye con constancia, paciencia e interés compuesto.</p>
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