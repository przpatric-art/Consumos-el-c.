import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
import datetime

# Función para formato moneda chilena
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(page_title="Generador de Boletas", page_icon="⚡")

# --- MENÚ LATERAL (SIDEBAR) ---
st.sidebar.header("📋 DATOS DEL CLIENTE")
nombre = st.sidebar.text_input("Nombre y Apellido", "Juan Pérez")
n_cliente = st.sidebar.text_input("Número de Cliente", "001")

st.sidebar.header("💰 VALORES EDITABLES (CÁLCULO INTERNO)")
# Ítems editables que NO aparecen en la boleta
precio_kwh = st.sidebar.number_input("1. Editar Valor por kWh ($)", min_value=0.0, value=150.0)
cobro_general = st.sidebar.number_input("2. Editar Cobro General ($)", min_value=0, value=0)

st.sidebar.header("📝 ITEMS DE LA BOLETA (VISIBLES)")
# Ítems que SÍ aparecen en la boleta
ant = st.sidebar.number_input("Lectura Anterior (kWh)", min_value=0)
actual = st.sidebar.number_input("Lectura Actual (kWh)", min_value=0)
cargo_lectura = st.sidebar.number_input("Valor Toma de Lectura ($)", min_value=0, value=1000)
# Cambio de nombre solicitado:
cobro_porton_camara = st.sidebar.number_input("Cobro por Portón y Cámara ($)", min_value=0, value=0)

# --- LÓGICA DE CÁLCULO INTERNO ---
consumo_mes = max(0, actual - ant)
subtotal_energia = round(consumo_mes * precio_kwh)

# El TOTAL suma todo (incluyendo los valores ocultos)
total_final = subtotal_energia + cobro_general + cargo_lectura + cobro_porton_camara

# --- INTERFAZ PRINCIPAL ---
st.title("⚡ Generador de Boleta")

st.subheader("Resumen de Cobro Actual")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Consumo", f"{consumo_mes} kWh")
c2.metric("Portón/Cámara", format_clp(cobro_porton_camara))
c3.metric("C. General", format_clp(cobro_general))
c4.metric("TOTAL", format_clp(total_final))

# --- GENERACIÓN DE IMAGEN (LA BOLETA) ---
def generar_imagen_final():
    ancho, alto = 500, 520
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Encabezado Negro
    draw.rectangle([0, 0, ancho, 80], fill=(0, 0, 0))
    draw.text((30, 25), "BOLETA DE COBRO ELÉCTRICO", fill=(255, 255, 255))
    
    # Datos Cliente
    y = 100
    draw.text((40, y), f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}", fill=(0, 0, 0))
    draw.text((40, y+30), f"Cliente: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, y+60), f"N. Cuenta: {n_cliente}", fill=(0, 0, 0))
    
    draw.line([40, 200, 460, 200], fill=(200, 200, 200), width=1)
    
    # Detalle que ve el cliente
    y_det = 230
    draw.text((40, y_det), "DETALLE DE CONSUMO Y SERVICIOS", fill=(100, 100, 100))
    
    draw.text((40, y_det+40), f"Consumo del mes:", fill=(0, 0, 0))
    draw.text((320, y_det+40), f"{consumo_mes} kWh", fill=(0, 0, 0))
    
    draw.text((40, y_det+70), "Cargo Toma de Lectura:", fill=(0, 0, 0))
    draw.text((320, y_det+70), format_clp(cargo_lectura), fill=(0, 0, 0))
    
    # Nuevo ítem visible en la boleta
    if cobro_porton_camara > 0:
        draw.text((40, y_det+100), "Cobro Portón y Cámara:", fill=(0, 0, 0))
        draw.text((320, y_det+100), format_clp(cobro_porton_camara), fill=(0, 0, 0))
    
    # RECUADRO TOTAL (Incluye los valores ocultos de cálculo)
    draw.rectangle([40, 390, 460, 460], outline=(0, 0, 0), width=2)
    draw.text((60, 415), "TOTAL A PAGAR", fill=(0, 0, 0))
    draw.text((320, 415), f"{format_clp(total_final)}", fill=(0, 0, 0))
    
    draw.text((120, 490), "Gracias por su pago puntual.", fill=(180, 180, 180))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- ACCIONES DE DESCARGA ---
st.divider()
img_boleta = generar_imagen_final()

col_img, col_xl = st.columns(2)
with col_img:
    st.download_button("🖼️ Descargar Imagen PNG", img_boleta, f"Boleta_{n_cliente}.png", "image/png")
with col_xl:
    # Registro interno detallado
    df = pd.DataFrame({
        "Concepto": ["Consumo kWh", "Precio kWh (Oculto)", "Cobro General (Oculto)", "Cargo Lectura", "Portón y Cámara", "Total Final"],
        "Monto": [consumo_mes, precio_kwh, cobro_general, cargo_lectura, cobro_porton_camara, total_final]
    })
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📊 Descargar Excel Interno", output.getvalue(), f"Control_{n_cliente}.xlsx")

st.image(img_boleta, caption="Vista previa de la boleta")
