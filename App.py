import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
import datetime

# Función para formato moneda chilena
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(page_title="Generador de Boletas Eléctricas", page_icon="⚡")

st.title("⚡ Sistema de Cobro Eléctrico")

# --- ENTRADA DE DATOS (SIDEBAR / MENÚ IZQUIERDO) ---
with st.sidebar:
    st.header("👤 Datos del Cliente")
    nombre = st.text_input("Nombre y Apellido", "Juan Pérez")
    n_cliente = st.text_input("Número de Cliente", "001")
    
    st.header("⚙️ Parámetros de Cobro (Editables)")
    # Casillas editables independientes
    precio_kwh = st.number_input("Valor por kWh ($)", min_value=0.0, value=150.0)
    cobro_general = st.number_input("Cobro General ($)", min_value=0, value=0)
    cargo_lectura = st.number_input("Valor por Toma de Lectura ($)", min_value=0, value=1000)
    cobros_extras = st.number_input("Cobros Extras ($)", min_value=0, value=0)
    
    st.header("📊 Lecturas")
    ant = st.number_input("Lectura Anterior (kWh)", min_value=0)
    actual = st.number_input("Lectura Actual (kWh)", min_value=0)

# --- LÓGICA DE CÁLCULO ---
consumo_mes = max(0, actual - ant)
monto_energia = round(consumo_mes * precio_kwh)

# Suma de todos los ítems editables
total_final = monto_energia + cobro_general + cargo_lectura + cobros_extras

# --- RESUMEN EN PANTALLA ---
st.subheader("Resumen del Cálculo")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Consumo", f"{consumo_mes} kWh")
c2.metric("Cobro General", format_clp(cobro_general))
c3.metric("Extras", format_clp(cobros_extras))
c4.metric("TOTAL", format_clp(total_final))

# --- FUNCIÓN PARA GENERAR LA IMAGEN ---
def crear_boleta_final(nombre, n_cliente, consumo, cargo_lec, extras, total):
    ancho, alto = 500, 520
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Encabezado
    draw.rectangle([0, 0, ancho, 80], fill=(45, 45, 45))
    draw.text((30, 25), "BOLETA DE CONSUMO ELÉCTRICO", fill=(255, 255, 255))
    
    # Datos de Identificación
    y_inicio = 110
    fecha_hoy = datetime.date.today().strftime('%d/%m/%Y')
    draw.text((40, y_inicio), f"Fecha: {fecha_hoy}", fill=(0, 0, 0))
    draw.text((40, y_inicio + 30), f"Cliente: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, y_inicio + 60), f"Número de Cliente: {n_cliente}", fill=(0, 0, 0))
    
    draw.line([40, 210, 460, 210], fill=(200, 200, 200), width=1)
    
    # DETALLE VISIBLE (Aquí se oculta el Cobro General y el Precio kWh)
    y_det = 240
    draw.text((40, y_det), "DETALLE DE COBRO", fill=(100, 100, 100))
    
    draw.text((40, y_det + 40), f"Consumo Registrado:", fill=(0, 0, 0))
    draw.text((320, y_det + 40), f"{consumo} kWh", fill=(0, 0, 0))
    
    draw.text((40, y_det + 70), "Cobro por Toma de Lectura:", fill=(0, 0, 0))
    draw.text((320, y_det + 70), format_clp(cargo_lec), fill=(0, 0, 0))
    
    if extras > 0:
        draw.text((40, y_det + 100), "Cobros Adicionales / Extras:", fill=(0, 0, 0))
        draw.text((320, y_det + 100), format_clp(extras), fill=(0, 0, 0))
    
    # TOTAL (Suma interna de todos los parámetros editables)
    draw.rectangle([40, 390, 460, 460], outline=(0, 0, 0), width=2)
    draw.text((60, 415), "TOTAL A PAGAR", fill=(0, 0, 0))
    draw.text((320, 415), f"{format_clp(total)}", fill=(0, 0, 0))
    
    draw.text((120, 490), "Comprobante digital para envío por RRSS", fill=(180, 180, 180))

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

# --- ACCIONES DE DESCARGA ---
st.divider()
boleta_img = crear_boleta_final(nombre, n_cliente, consumo_mes, cargo_lectura, cobros_extras, total_final)

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="🖼️ Descargar Imagen para RRSS",
        data=boleta_img,
        file_name=f"Boleta_{n_cliente}.png",
        mime="image/png"
    )
with col2:
    # El Excel incluye el Cobro General para tu control
    df_registro = pd.DataFrame({
        "Concepto": ["Consumo kWh", "Precio kWh (Interno)", "Cobro General (Interno)", "Toma Lectura", "Extras", "Total Final"],
        "Valor": [consumo_mes, format_clp(precio_kwh), format_clp(cobro_general), format_clp(cargo_lectura), format_clp(cobros_extras), format_clp(total_final)]
    })
    buffer_ex = BytesIO()
    with pd.ExcelWriter(buffer_ex, engine='openpyxl') as writer:
        df_registro.to_excel(writer, index=False)
    st.download_button(
        label="📊 Descargar Excel Interno",
        data=buffer_ex.getvalue(),
        file_name=f"Registro_{n_cliente}.xlsx"
    )

st.image(boleta_img, caption="Vista previa de la boleta")
