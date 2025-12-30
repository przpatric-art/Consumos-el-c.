import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import datetime
import random

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Generador Pro ⚡", page_icon="⚡", layout="wide")

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
precio_kwh = st.sidebar.number_input("Precio por kWh ($)", min_value=0.0, value=155.2)
cargo_fijo = st.sidebar.number_input("Cargo Fijo / Lectura ($)", min_value=0, value=1200)
otros_cargos = st.sidebar.number_input("Otros Cargos (Portón/Cámaras/Etc)", min_value=0, value=0)

# --- LÓGICA DE NEGOCIO ---
consumo_mes = actual - ant
if consumo_mes < 0:
    st.error("⚠️ Error: La lectura actual no puede ser menor a la anterior.")
    consumo_mes = 0

monto_energia = round(consumo_mes * precio_kwh)
total_final = monto_energia + cargo_fijo + otros_cargos
folio = random.randint(10000, 99999)

# --- CUERPO PRINCIPAL ---
st.title("⚡ Sistema de Facturación Eléctrica")

col_a, col_b = st.columns([1, 2])

with col_a:
    st.subheader("Resumen de Cuenta")
    st.metric("Total a Pagar", format_clp(total_final))
    st.metric("Consumo del Mes", f"{consumo_mes} kWh", delta=f"{consumo_mes} kWh" if consumo_mes > 0 else None)
    
    with st.expander("Ver desglose de costos"):
        st.write(f"Energía: {format_clp(monto_energia)}")
        st.write(f"Cargos Fijos: {format_clp(cargo_fijo)}")
        st.write(f"Otros: {format_clp(otros_cargos)}")

with col_b:
    # Gráfico simple de comparación
    st.subheader("Histórico de Consumo (kWh)")
    data_grafico = pd.DataFrame({
        "Mes": ["Anterior", "Actual"],
        "kWh": [ant * 0.1, consumo_mes] # Simulación de histórico
    })
    st.bar_chart(data=data_grafico, x="Mes", y="kWh")

# --- FUNCIÓN GENERAR IMAGEN ---
def generar_boleta_pro():
    ancho, alto = 600, 800
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font_tit = ImageFont.truetype("arial.ttf", 28)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_std = ImageFont.truetype("arial.ttf", 16)
        font_bold = ImageFont.truetype("arial.ttf", 18)
    except:
        font_tit = font_sub = font_std = font_bold = ImageFont.load_default()

    # Encabezado con degradado o bloque sólido
    draw.rectangle([0, 0, ancho, 120], fill=(20, 40, 80))
    draw.text((40, 30), "ESTADO DE CUENTA ELÉCTRICA", fill=(255, 255, 255), font=font_tit)
    draw.text((40, 75), f"Folio N°: {folio} | Cliente: {n_cliente}", fill=(200, 200, 200), font=font_std)

    # Bloque Datos Cliente
    draw.text((40, 150), "DETALLES DEL CLIENTE", fill=(20, 40, 80), font=font_bold)
    draw.text((40, 180), f"Nombre: {nombre.upper()}", fill=(0,0,0), font=font_std)
    draw.text((40, 205), f"Fecha Emisión: {fecha_emision.strftime('%d/%m/%Y')}", fill=(0,0,0), font=font_std)
    draw.text((320, 205), f"Vencimiento: {fecha_vence.strftime('%d/%m/%Y')}", fill=(200, 0, 0), font=font_bold)

    # Detalle de Consumo (Tabla)
    draw.rectangle([40, 250, 560, 290], fill=(240, 240, 240))
    draw.text((50, 260), "DESCRIPCIÓN", fill=(0,0,0), font=font_bold)
    draw.text((450, 260), "VALOR", fill=(0,0,0), font=font_bold)

    y_pos = 310
    items = [
        (f"Consumo Energía ({consumo_mes} kWh x ${precio_kwh})", format_clp(monto_energia)),
        ("Cargo Fijo / Administración", format_clp(cargo_fijo)),
        ("Servicios Adicionales (Cámaras/Portón)", format_clp(otros_cargos)),
    ]

    for item, valor in items:
        draw.text((50, y_pos), item, fill=(50, 50, 50), font=font_std)
        draw.text((450, y_pos), valor, fill=(0, 0, 0), font=font_std)
        y_pos += 40

    # Línea de Total
    draw.line([40, 450, 560, 450], fill=(20, 40, 80), width=2)
    draw.text((50, 470), "TOTAL A PAGAR", fill=(20, 40, 80), font=font_tit)
    draw.text((420, 470), format_clp(total_final), fill=(0,0,0), font=font_tit)

    # Pie de página / Mensaje
    draw.rectangle([0, 750, ancho, 800], fill=(240, 240, 240))
    msg = "Corte de servicio tras 2 facturas vencidas. Evite recargos."
    draw.text((120, 765), msg, fill=(100, 100, 100), font=font_std)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- BOTONES DE ACCIÓN ---
st.divider()
img_final = generar_boleta_pro()

col1, col2, col3 = st.columns(3)
with col1:
    st.download_button("📩 Descargar Boleta (PNG)", data=img_final, file_name=f"Boleta_{n_cliente}_{folio}.png")
with col2:
    # Preparar Excel
    resumen = {
        "Folio": [folio], "Cliente": [nombre], "Consumo kWh": [consumo_mes],
        "Total": [total_final], "Vencimiento": [fecha_vence]
    }
    df = pd.DataFrame(resumen)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📊 Exportar a Excel", data=output.getvalue(), file_name=f"Registro_{fecha_emision}.xlsx")

st.image(img_final, caption="Vista previa del documento oficial", use_container_width=True)
