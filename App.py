import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Generador de Boletas ⚡", page_icon="⚡", layout="centered")

# Función para formato moneda chilena
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

# --- SIDEBAR: ENTRADA DE DATOS ---
st.sidebar.header("📋 DATOS DEL CLIENTE")
nombre = st.sidebar.text_input("Nombre y Apellido", "Juan Pérez")
n_cliente = st.sidebar.text_input("Número de Cliente/Cuenta", "123456")
fecha_emision = st.sidebar.date_input("Fecha de Emisión", datetime.date.today())
fecha_vence = st.sidebar.date_input("Fecha de Vencimiento", datetime.date.today() + datetime.timedelta(days=15))

st.sidebar.divider()
st.sidebar.header("📏 MEDICIÓN")
ant = st.sidebar.number_input("Lectura Anterior (kWh)", min_value=0, value=1200)
actual = st.sidebar.number_input("Lectura Actual (kWh)", min_value=0, value=1350)

st.sidebar.divider()
st.sidebar.header("💰 TARIFAS Y CARGOS")
precio_kwh = st.sidebar.number_input("Precio por kWh ($)", min_value=0.0, value=155.0)
cargo_fijo = st.sidebar.number_input("Cargo Fijo / Lectura ($)", min_value=0, value=1000)
otros_cargos = st.sidebar.number_input("Otros Cargos (Portón/Cámaras/Etc)", min_value=0, value=0)

# --- LÓGICA DE CÁLCULO (CORREGIDA) ---
consumo_mes = actual - ant

# Validación para evitar consumos negativos
if consumo_mes < 0:
    st.error("⚠️ La lectura actual es menor a la anterior. Por favor revisa los datos.")
    consumo_mes = 0

monto_energia = round(consumo_mes * precio_kwh)
# Aquí se usa 'cargo_fijo' para evitar el NameError
total_final = monto_energia + cargo_fijo + otros_cargos
folio = random.randint(10000, 99999)

# --- INTERFAZ PRINCIPAL ---
st.title("⚡ Generador de Boleta Eléctrica")

# Resumen rápido en pantalla
st.subheader("Resumen del Cobro")
c1, c2, c3 = st.columns(3)
c1.metric("Consumo Mes", f"{consumo_mes} kWh")
c2.metric("Vencimiento", fecha_vence.strftime('%d/%m/%Y'))
c3.metric("TOTAL A PAGAR", format_clp(total_final))

# --- FUNCIÓN PARA GENERAR LA IMAGEN ---
def generar_boleta_pro():
    ancho, alto = 600, 750
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Manejo de fuentes para evitar errores en diferentes sistemas
    try:
        font_tit = ImageFont.truetype("arial.ttf", 28)
        font_std = ImageFont.truetype("arial.ttf", 16)
        font_bold = ImageFont.truetype("arial.ttf", 18)
    except:
        font_tit = font_std = font_bold = ImageFont.load_default()

    # Diseño: Encabezado
    azul_oscuro = (20, 40, 80)
    draw.rectangle([0, 0, ancho, 120], fill=azul_oscuro)
    draw.text((40, 30), "BOLETA DE COBRO ELÉCTRICO", fill=(255, 255, 255), font=font_tit)
    draw.text((40, 75), f"Folio N°: {folio} | N° Cuenta: {n_cliente}", fill=(200, 200, 200), font=font_std)

    # Información del Cliente
    draw.text((40, 150), "INFORMACIÓN DEL CLIENTE", fill=azul_oscuro, font=font_bold)
    draw.text((40, 180), f"Nombre: {nombre.upper()}", fill=(0,0,0), font=font_std)
    draw.text((40, 205), f"Fecha Emisión: {fecha_emision.strftime('%d/%m/%Y')}", fill=(0,0,0), font=font_std)
    draw.text((320, 205), f"Vencimiento: {fecha_vence.strftime('%d/%m/%Y')}", fill=(200, 0, 0), font=font_bold)

    # Tabla de Detalle
    draw.rectangle([40, 260, 560, 300], fill=(240, 240, 240))
    draw.text((50, 270), "DESCRIPCIÓN", fill=(0,0,0), font=font_bold)
    draw.text((450, 270), "MONTO", fill=(0,0,0), font=font_bold)

    y_pos = 320
    items = [
        (f"Energía ({consumo_mes} kWh x ${precio_kwh})", format_clp(monto_energia)),
        ("Toma de Lectura / Cargo Fijo", format_clp(cargo_fijo)),
        ("Servicios Comunidad (Otros)", format_clp(otros_cargos)),
    ]

    for item, valor in items:
        draw.text((50, y_pos), item, fill=(50, 50, 50), font=font_std)
        draw.text((450, y_pos), valor, fill=(0, 0, 0), font=font_std)
        y_pos += 40

    # Línea de Total
    draw.line([40, 480, 560, 480], fill=azul_oscuro, width=2)
    draw.text((50, 500), "TOTAL A PAGAR", fill=azul_oscuro, font=font_tit)
    draw.text((420, 500), format_clp(total_final), fill=(0,0,0), font=font_tit)

    # Pie de página
    draw.text((150, 700), "Favor realizar el pago antes del vencimiento.", fill=(150, 150, 150), font=font_std)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- ACCIONES DE DESCARGA ---
st.divider()
img_final = generar_boleta_pro()

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="🖼️ Descargar Boleta (PNG)",
        data=img_final,
        file_name=f"Boleta_{n_cliente}_{folio}.png",
        mime="image/png"
    )
with col2:
    # Generar Excel de registro
    df_excel = pd.DataFrame({
        "Folio": [folio], 
        "Cliente": [nombre], 
        "Consumo kWh": [consumo_mes], 
        "Total CLP": [total_final],
        "Fecha": [fecha_emision]
    })
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_excel.to_excel(writer, index=False)
    st.download_button(
        label="📊 Guardar en Excel",
        data=output.getvalue(),
        file_name=f"Registro_{n_cliente}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Previsualización final
st.image(img_final, caption="Previsualización de la boleta generada", use_container_width=True)
