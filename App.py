import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import datetime

def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(page_title="Generador de Boletas Eléctricas", page_icon="⚡")

# --- SIDEBAR ---
st.sidebar.header("📋 DATOS DEL CLIENTE")
nombre = st.sidebar.text_input("Nombre y Apellido", "Juan Pérez")
n_cliente = st.sidebar.text_input("Número de Cliente", "001")

st.sidebar.header("💰 VALORES DE CÁLCULO")
precio_kwh = st.sidebar.number_input("Precio por kWh ($)", min_value=0.0, value=150.0)

st.sidebar.header("📝 ITEMS DE LA BOLETA")
ant = st.sidebar.number_input("Lectura Anterior (kWh)", min_value=0)
actual = st.sidebar.number_input("Lectura Actual (kWh)", min_value=0)
cargo_lectura = st.sidebar.number_input("Valor Toma de Lectura ($)", min_value=0, value=1000)
cobro_porton_camara = st.sidebar.number_input("Cobro Portón/Cámara ($)", min_value=0, value=0)
cobro_general = st.sidebar.number_input("Otros Cobros ($)", min_value=0, value=0)

# --- LÓGICA ---
consumo_mes = max(0, actual - ant)
subtotal_energia = round(consumo_mes * precio_kwh)
total_final = subtotal_energia + cobro_general + cargo_lectura + cobro_porton_camara

# --- INTERFAZ ---
st.title("⚡ Generador de Boleta")

def generar_imagen_final():
    ancho, alto = 500, 600
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    azul_oscuro = (26, 54, 104)
    gris_oscuro = (50, 50, 50)

    # 1. ENCABEZADO
    draw.rectangle([0, 0, ancho, 110], fill=azul_oscuro)
    draw.text((30, 40), "BOLETA DE COBRO ELÉCTRICO", fill=(255, 255, 255))

    # 2. INFO CLIENTE
    y = 130
    fecha_hoy = datetime.date.today().strftime('%d/%m/%Y')
    draw.text((40, y), f"Fecha de Emisión: {fecha_hoy}", fill=gris_oscuro)
    draw.text((40, y+30), f"CLIENTE: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, y+55), f"N° CUENTA: {n_cliente}", fill=(0, 0, 0))

    # 3. DETALLE
    y_det = 240
    draw.text((40, y_det), "DETALLE DEL CONSUMO", fill=azul_oscuro)
    draw.line([40, y_det+25, 460, y_det+25], fill=(200, 200, 200), width=1)

    items = [
        ("Lectura Actual:", f"{actual} kWh"),
        ("Lectura Anterior:", f"{ant} kWh"),
        ("Consumo del Mes:", f"{consumo_mes} kWh"),
        ("-" * 40, ""),
        ("Subtotal Energía:", format_clp(subtotal_energia)),
        ("Cargo Lectura:", format_clp(cargo_lectura)),
        ("Portón y Cámara:", format_clp(cobro_porton_camara)),
        ("Otros cargos:", format_clp(cobro_general))
    ]

    for i, (label, value) in enumerate(items):
        pos_y = y_det + 50 + (i * 30)
        draw.text((40, pos_y), label, fill=gris_oscuro)
        draw.text((350, pos_y), value, fill=(0, 0, 0))

    # 4. TOTAL
    draw.rectangle([30, 500, 470, 560], outline=azul_oscuro, width=2)
    draw.text((50, 520), "TOTAL A PAGAR", fill=azul_oscuro)
    draw.text((350, 520), format_clp(total_final), fill=(0, 0, 0))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# Mostrar métricas
st.subheader("Resumen de Cobro")
col1, col2 = st.columns(2)
col1.metric("Consumo Mes", f"{consumo_mes} kWh")
col2.metric("Total a Pagar", format_clp(total_final))

# Previsualización y Descarga
img_boleta = generar_imagen_final()
st.image(img_boleta, caption="Vista previa de la boleta")

st.download_button(
    label="📥 Descargar Boleta (PNG)",
    data=img_boleta,
    file_name=f"Boleta_{n_cliente}_{nombre.replace(' ', '_')}.png",
    mime="image/png"
)
