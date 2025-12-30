import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
import datetime

# --- FUNCIONES DE UTILIDAD ---
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(page_title="Gestor Electrico Pro", page_icon="⚡", layout="wide")

# --- ESTADO DE LA APP (BASE DE DATOS TEMPORAL) ---
if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = pd.DataFrame(columns=["Nombre", "N_Cliente", "Lectura_Anterior", "Lectura_Actual"])

# --- LOGICA DE CARGA DE EXCEL PREVIO ---
st.sidebar.header("📂 CARGAR DATOS PREVIOS")
uploaded_file = st.sidebar.file_uploader("Subir Excel del mes anterior", type=["xlsx"])

datos_previos = {}
if uploaded_file:
    try:
        df_importado = pd.read_excel(uploaded_file)
        for _, row in df_importado.iterrows():
            datos_previos[str(row['N_Cliente'])] = {
                "Nombre": row['Nombre'],
                "Lectura_Anterior": row['Lectura_Actual']
            }
        st.sidebar.success("Datos cargados correctamente")
    except Exception as e:
        st.sidebar.error("Error al leer el archivo")

# --- MENU LATERAL ---
with st.sidebar:
    st.title("Panel de Control")
    
    with st.expander("👤 Datos del Cliente", expanded=True):
        n_cliente_input = st.text_input("Numero de Cliente", "001")
        
        nombre_def = "Juan Perez"
        lectura_ant_def = 0
        
        if n_cliente_input in datos_previos:
            nombre_def = datos_previos[n_cliente_input]["Nombre"]
            lectura_ant_def = int(datos_previos[n_cliente_input]["Lectura_Anterior"])
            st.caption(f"✅ Cliente encontrado. Lectura anterior sugerida: {lectura_ant_def}")

        nombre = st.text_input("Nombre y Apellido", nombre_def)
    
    with st.expander("⚙️ Configuracion", expanded=False):
        precio_kwh = st.number_input("Valor por kWh ($)", min_value=0.0, value=150.0)
        cobro_general = st.number_input("Cobro General ($)", min_value=0, value=0)
    
    with st.expander("📊 Lecturas y Cargos", expanded=True):
        ant = st.number_input("Lectura Anterior (kWh)", min_value=0, value=lectura_ant_def)
        actual = st.number_input("Lectura Actual (kWh)", min_value=0)
        cargo_lectura = st.number_input("Valor Toma de Lectura ($)", min_value=0, value=1000)
        # Cambio solicitado: Gasto Comun
        gasto_comun = st.number_input("Gasto Comun ($)", min_value=0, value=0)

# --- CALCULOS ---
consumo_mes = max(0, actual - ant)
subtotal_energia = round(consumo_mes * precio_kwh)
total_final = subtotal_energia + cobro_general + cargo_lectura + gasto_comun

# --- ACCION: GUARDAR EN BASE DE DATOS ---
if st.sidebar.button("💾 GUARDAR REGISTRO Y GENERAR"):
    nuevo_registro = pd.DataFrame({
        "Nombre": [nombre],
        "N_Cliente": [n_cliente_input],
        "Lectura_Anterior": [ant],
        "Lectura_Actual": [actual]
    })
    st.session_state.db_clientes = st.session_state.db_clientes[st.session_state.db_clientes.N_Cliente != n_cliente_input]
    st.session_state.db_clientes = pd.concat([st.session_state.db_clientes, nuevo_registro], ignore_index=True)
    st.toast(f"Registro de {nombre} guardado")

# --- CUERPO PRINCIPAL ---
st.title("⚡ Generador de Boletas Profesionales")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1: st.metric("Consumo", f"{consumo_mes} kWh")
with col_m2: st.metric("Gasto Comun", format_clp(gasto_comun))
with col_m3: st.metric("Clientes Procesados", len(st.session_state.db_clientes))
with col_m4: st.metric("TOTAL FINAL", format_clp(total_final))

st.markdown("---")

# Visualizacion y Descarga
col_preview, col_actions = st.columns([2, 1])

def generar_imagen_final():
    ancho, alto = 500, 550
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    azul_oscuro = (26, 54, 104) 
    
    # Encabezado
    draw.rectangle([0, 0, ancho, 100], fill=azul_oscuro)
    draw.text((30, 40), "BOLETA DE COBRO ELECTRICO", fill=(255, 255, 255))
    
    # Datos Cliente
    y = 130
    fecha_hoy = datetime.date.today().strftime('%d/%m/%Y')
    draw.text((40, y), f"Fecha de Emision: {fecha_hoy}", fill=(50, 50, 50))
    draw.text((40, y+30), f"CLIENTE: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, y+60), f"N. CUENTA: {n_cliente_input}", fill=(0, 0, 0))
    
    draw.line([40, 230, 460, 230], fill=(200, 200, 200), width=1)
    
    # Detalles
    y_det = 250
    draw.text((40, y_det), "DETALLE DE CONSUMO Y SERVICIOS", fill=azul_oscuro)
    draw.text((40, y_det+40), "Consumo registrado en el mes:", fill=(50, 50, 50))
    draw.text((350, y_det+40), f"{consumo_mes} kWh", fill=(0, 0, 0))
    
    draw.text((40, y_det+70), "Cargo Toma de Lectura:", fill=(50, 50, 50))
    draw.text((350, y_det+70), format_clp(cargo_lectura), fill=(0, 0, 0))
    
    if gasto_comun > 0:
        draw.text((40, y_det+100), "Gasto Comun:", fill=(50, 50, 50))
        draw.text((350, y_det+100), format_clp(gasto_comun), fill=(0, 0, 0))
    
    # Total
    draw.rectangle([30, 410, 470, 480], outline=azul_oscuro, width=2)
    draw.text((50, 435), "TOTAL A PAGAR", fill=azul_oscuro)
    draw.text((350, 435), f"{format_clp(total_final)}", fill=(0, 0, 0))
    
    draw.text((140, 510), "Gracias por su pago puntual.", fill=(150, 150, 150))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

with col_preview:
    st.subheader("🖼️ Vista Previa")
    img_boleta = generar_imagen_final()
    st.image(img_boleta, use_container_width=True)

with col_actions:
    st.subheader("📥 Exportar")
    st.download_button("Descargar Boleta (Imagen)", img_boleta, f"Boleta_{n_cliente_input}.png", "image/png")
    
    if not st.session_state.db_clientes.empty:
        buffer_all = BytesIO()
        with pd.ExcelWriter(buffer_all, engine='openpyxl') as writer:
            st.session_state.db_clientes.to_excel(writer, index=False)
        
        st.download_button(
            label="Descargar Base de Datos (Excel)",
            data=buffer_all.getvalue(),
            file_name=f"Base_Datos_Electricidad.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    st.info("Al guardar cada cliente, se acumulan en la base de datos para descargarla al final.")
