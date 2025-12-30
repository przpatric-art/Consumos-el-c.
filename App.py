import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
import datetime

# --- FUNCIONES DE UTILIDAD ---
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

# Configuración de página con tema oscuro/claro automático
st.set_page_config(
    page_title="Gestor Electrico Pro",
    page_icon="⚡",
    layout="wide"
)

# --- ESTILO PERSONALIZADO (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div.stButton > button:first-child {
        background-color: #1a3668;
        color: white;
        width: 100%;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MENÚ LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/355/355980.png", width=80)
    st.title("Panel de Control")
    
    with st.expander("👤 Datos del Cliente", expanded=True):
        nombre = st.text_input("Nombre y Apellido", "Juan Perez")
        n_cliente = st.text_input("Numero de Cliente", "001")
    
    with st.expander("⚙️ Configuracion de Tarifas", expanded=False):
        precio_kwh = st.number_input("Valor por kWh ($)", min_value=0.0, value=150.0)
        cobro_general = st.number_input("Cobro General ($)", min_value=0, value=0)
    
    with st.expander("📊 Lecturas de Medidor", expanded=True):
        ant = st.number_input("Lectura Anterior (kWh)", min_value=0)
        actual = st.number_input("Lectura Actual (kWh)", min_value=0)
        cargo_lectura = st.number_input("Valor Toma de Lectura ($)", min_value=0, value=1000)
        cobro_porton_camara = st.number_input("Porton y Camara ($)", min_value=0, value=0)

# --- CÁLCULOS ---
consumo_mes = max(0, actual - ant)
subtotal_energia = round(consumo_mes * precio_kwh)
total_final = subtotal_energia + cobro_general + cargo_lectura + cobro_porton_camara

# --- CUERPO PRINCIPAL ---
st.title("⚡ Generador de Boletas Profesionales")
st.info("Complete los datos en el panel izquierdo para actualizar el resumen y la boleta.")

# Tarjetas de Resumen
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Consumo Registrado", f"{consumo_mes} kWh")
with col_m2:
    st.metric("Servicios Adicionales", format_clp(cobro_porton_camara + cargo_lectura))
with col_m3:
    st.metric("Cargos Base", format_clp(cobro_general))
with col_m4:
    st.metric("TOTAL A COBRAR", format_clp(total_final))

st.markdown("---")

# Sección de Visualización y Descarga
col_preview, col_actions = st.columns([2, 1])

def generar_imagen_final():
    ancho, alto = 500, 550
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    azul_oscuro = (26, 54, 104) 
    
    draw.rectangle([0, 0, ancho, 100], fill=azul_oscuro)
    draw.text((30, 40), "BOLETA DE COBRO ELECTRICO", fill=(255, 255, 255))
    
    y = 130
    fecha_hoy = datetime.date.today().strftime('%d/%m/%Y')
    draw.text((40, y), f"Fecha de Emision: {fecha_hoy}", fill=(50, 50, 50))
    draw.text((40, y+30), f"CLIENTE: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, y+60), f"N. CUENTA: {n_cliente}", fill=(0, 0, 0))
    
    draw.line([40, 230, 460, 230], fill=(200, 200, 200), width=1)
    
    y_det = 250
    draw.text((40, y_det), "DETALLE DE CONSUMO Y SERVICIOS", fill=azul_oscuro)
    draw.text((40, y_det+40), "Consumo registrado en el mes:", fill=(50, 50, 50))
    draw.text((350, y_det+40), f"{consumo_mes} kWh", fill=(0, 0, 0))
    draw.text((40, y_det+70), "Cargo Toma de Lectura:", fill=(50, 50, 50))
    draw.text((350, y_det+70), format_clp(cargo_lectura), fill=(0, 0, 0))
    
    if cobro_porton_camara > 0:
        draw.text((40, y_det+100), "Cobro Porton y Camara:", fill=(50, 50, 50))
        draw.text((350, y_det+100), format_clp(cobro_porton_camara), fill=(0, 0, 0))
    
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
    st.download_button(
        label="Descargar Imagen para WhatsApp",
        data=img_boleta,
        file_name=f"Boleta_{n_cliente}.png",
        mime="image/png"
    )
    
    df = pd.DataFrame({
        "Concepto": ["Consumo kWh", "Precio kWh", "Cobro General", "Toma Lectura", "Porton/Camara", "Total"],
        "Valor": [consumo_mes, precio_kwh, cobro_general, cargo_lectura, cobro_porton_camara, total_final]
    })
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="Descargar Reporte Excel",
        data=output.getvalue(),
        file_name=f"Reporte_{n_cliente}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.success("Cálculo actualizado automáticamente")
