import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
import datetime

# --- FUNCIONES DE CONFIGURACIÓN ---
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(
    page_title="Consumo Eléctrico Pro",
    page_icon="⚡",
    layout="wide"
)

# --- ESTILO CSS PROFESIONAL ---
st.markdown("""
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #f4f7f9;
    }
    /* Estilo de métricas */
    [data-testid="stMetricValue"] {
        color: #1a3668;
        font-size: 24px;
    }
    /* Botones principales */
    .stButton>button {
        background-color: #1a3668;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #d4af37;
        color: #1a3668;
        font-weight: bold;
    }
    /* Contenedores */
    .css-1r6slb0 {
        padding: 20px;
        border-radius: 15px;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE LA APP ---
if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = pd.DataFrame(columns=["Nombre", "N_Cliente", "Lectura_Anterior", "Lectura_Actual"])

# --- SIDEBAR (PANEL DE CONTROL) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #1a3668;'>⚡ Control Pro</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("📂 Carga Histórica")
    uploaded_file = st.file_uploader("Importar Excel anterior", type=["xlsx"])

    datos_previos = {}
    if uploaded_file:
        try:
            df_importado = pd.read_excel(uploaded_file)
            for _, row in df_importado.iterrows():
                datos_previos[str(row['N_Cliente'])] = {
                    "Nombre": row['Nombre'],
                    "Lectura_Anterior": row['Lectura_Actual']
                }
            st.success("Historial cargado con éxito")
        except:
            st.error("Archivo no compatible")

    st.markdown("---")
    st.subheader("👤 Datos Cliente")
    n_cliente_input = st.text_input("N° Cliente", "001")
    
    nombre_def = "Juan Perez"
    lectura_ant_def = 0
    if n_cliente_input in datos_previos:
        nombre_def = datos_previos[n_cliente_input]["Nombre"]
        lectura_ant_def = int(datos_previos[n_cliente_input]["Lectura_Anterior"])
    
    nombre = st.text_input("Nombre Completo", nombre_def)
    
    st.subheader("⚙️ Configuración y Lecturas")
    precio_kwh = st.number_input("Precio kWh ($)", value=150.0)
    cobro_general = st.number_input("Cobro General ($)", value=0)
    
    ant = st.number_input("Lectura Anterior", value=lectura_ant_def)
    actual = st.number_input("Lectura Actual", value=0)
    
    cargo_lectura = st.number_input("Toma Lectura ($)", value=1000)
    gasto_comun = st.number_input("Gasto Comun ($)", value=0)

    st.markdown("---")
    if st.button("💾 GUARDAR REGISTRO"):
        nuevo = pd.DataFrame({"Nombre": [nombre], "N_Cliente": [n_cliente_input], 
                              "Lectura_Anterior": [ant], "Lectura_Actual": [actual]})
        st.session_state.db_clientes = st.session_state.db_clientes[st.session_state.db_clientes.N_Cliente != n_cliente_input]
        st.session_state.db_clientes = pd.concat([st.session_state.db_clientes, nuevo], ignore_index=True)
        st.toast(f"Guardado: {nombre}", icon="✅")

# --- LÓGICA DE CÁLCULO ---
consumo_mes = max(0, actual - ant)
monto_energia = round(consumo_mes * precio_kwh)
total_final = monto_energia + cobro_general + cargo_lectura + gasto_comun

# --- ÁREA PRINCIPAL ---
col_t1, col_t2 = st.columns([2, 1])

with col_t1:
    st.markdown(f"<h2 style='color: #1a3668;'>Resumen de Cobro: {nombre}</h2>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Consumo", f"{consumo_mes} kWh")
    m2.metric("Gasto Comun", format_clp(gasto_comun))
    m3.metric("Energía", format_clp(monto_energia))
    m4.metric("TOTAL", format_clp(total_final))

with col_t2:
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.db_clientes.empty:
        buffer_excel = BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            st.session_state.db_clientes.to_excel(writer, index=False)
        st.download_button("📊 DESCARGAR EXCEL MES ACTUAL", buffer_excel.getvalue(), 
                           "Base_Datos_Consumo.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")

# --- GENERACIÓN DE BOLETA ---
def generar_boleta_premium():
    ancho, alto = 500, 580
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    azul_cobalto = (26, 54, 104)
    dorado = (212, 175, 55)
    gris_suave = (245, 245, 245)
    
    # Diseño Superior
    draw.rectangle([0, 0, ancho, 120], fill=azul_cobalto)
    draw.rectangle([0, 110, ancho, 120], fill=dorado) # Línea dorada decorativa
    draw.text((35, 45), "BOLETA DE COBRO ELECTRICO", fill=(255, 255, 255))
    
    # Cuerpo
    fecha = datetime.date.today().strftime('%d/%m/%Y')
    draw.text((40, 150), f"Fecha Emision: {fecha}", fill=(100, 100, 100))
    draw.text((40, 185), f"CLIENTE: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, 215), f"N. CUENTA: {n_cliente_input}", fill=(0, 0, 0))
    
    draw.line([40, 260, 460, 260], fill=(220, 220, 220), width=1)
    
    # Detalle
    draw.text((40, 280), "DETALLE DE SERVICIOS", fill=azul_cobalto)
    
    y_items = 330
    items = [
        ("Consumo registrado:", f"{consumo_mes} kWh"),
        ("Cargo Toma de Lectura:", format_clp(cargo_lectura)),
        ("Gasto Comun:", format_clp(gasto_comun))
    ]
    
    for label, value in items:
        draw.text((40, y_items), label, fill=(50, 50, 50))
        draw.text((350, y_items), value, fill=(0, 0, 0))
        y_items += 40
    
    # Caja de Total
    draw.rectangle([40, 460, 460, 530], fill=gris_suave, outline=dorado, width=2)
    draw.text((60, 485), "TOTAL A PAGAR", fill=azul_cobalto)
    draw.text((330, 485), format_clp(total_final), fill=(0, 0, 0))
    
    draw.text((150, 550), "Gracias por su pago puntual", fill=(180, 180, 180))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

col_img, col_info = st.columns([1, 1])

with col_img:
    img_bytes = generar_boleta_premium()
    st.image(img_bytes, caption="Vista Previa de Boleta Premium")

with col_info:
    st.subheader("🚀 Acciones Rápidas")
    st.download_button("📥 DESCARGAR BOLETA PNG", img_bytes, f"Boleta_{n_cliente_input}.png", "image/png")
    st.markdown("""
    **Instrucciones de flujo:**
    1. Ingrese los datos del cliente.
    2. Revise el total calculado.
    3. Haga clic en **'Guardar Registro'** para añadir a la lista.
    4. Descargue la imagen para enviar por WhatsApp.
    5. Al finalizar el día, descargue el **Excel acumulado**.
    """)
    
    if not st.session_state.db_clientes.empty:
        with st.expander("📝 Clientes procesados en esta sesión"):
            st.dataframe(st.session_state.db_clientes, use_container_width=True)
