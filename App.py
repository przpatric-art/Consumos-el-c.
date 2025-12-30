import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import datetime

# Función para formato moneda chilena
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(page_title="Generador de Boletas", page_icon="⚡")

st.title("⚡ Cobro Eléctrico Pro")

# --- ENTRADA DE DATOS ---
with st.sidebar:
    st.header("Configuración")
    nombre = st.text_input("Nombre del Cliente", "Juan Pérez")
    n_cliente = st.text_input("N° de Cliente", "123456")
    ant = st.number_input("Lectura Anterior", min_value=0)
    actual = st.number_input("Lectura Actual", min_value=0)
    precio_kwh = st.number_input("Precio kWh ($)", min_value=0.0, value=150.0)
    cargo_fijo = st.number_input("Cargo Lectura ($)", min_value=0, value=1000)

# Cálculos
consumo = max(0, actual - ant)
subtotal = round(consumo * precio_kwh)
total = subtotal + cargo_fijo

# Mostrar Resumen en Pantalla
st.subheader("Resumen del Cobro")
col1, col2 = st.columns(2)
col1.metric("Consumo (kWh)", f"{consumo} kWh")
col2.metric("Total a Pagar", format_clp(total))

# --- FUNCIÓN PARA GENERAR IMAGEN ESTILIZADA ---
def crear_imagen_pro(nombre, n_cliente, consumo, total, precio_kwh, cargo_fijo):
    # Crear lienzo (Ancho x Alto)
    ancho, alto = 500, 600
    img = Image.new('RGB', (ancho, alto), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    
    # Dibujar Encabezado Azul
    draw.rectangle([0, 0, ancho, 100], fill=(0, 51, 102))
    draw.text((20, 35), "COMPROBANTE DE CONSUMO", fill=(255, 255, 255))
    
    # Cuerpo de la boleta
    y = 130
    draw.text((30, y), f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}", fill=(0, 0, 0))
    draw.text((30, y+30), f"Cliente: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((30, y+60), f"N. Cuenta: {n_cliente}", fill=(0, 0, 0))
    
    # Línea divisoria
    draw.line([30, 230, 470, 230], fill=(200, 200, 200), width=2)
    
    # Detalles
    y_det = 250
    draw.text((30, y_det), "Detalle del Consumo", fill=(0, 51, 102))
    draw.text((30, y_det+40), f"Consumo del Mes: {consumo} kWh", fill=(50, 50, 50))
    draw.text((30, y_det+70), f"Valor por kWh: {format_clp(precio_kwh)}", fill=(50, 50, 50))
    draw.text((30, y_det+100), f"Cargo Toma Lectura: {format_clp(cargo_fijo)}", fill=(50, 50, 50))
    
    # Recuadro de Total
    draw.rectangle([30, 420, 470, 500], outline=(0, 51, 102), width=3)
    draw.text((50, 450), "TOTAL A PAGAR:", fill=(0, 51, 102))
    draw.text((300, 450), f"{format_clp(total)}", fill=(0, 0, 0))
    
    draw.text((150, 550), "¡Gracias por su pago oportuno!", fill=(100, 100, 100))

    # Guardar imagen en buffer
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- BOTONES DE DESCARGA ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    # Generar Excel
    output = BytesIO()
    df = pd.DataFrame({
        "Concepto": ["Consumo", "Precio kWh", "Cargo", "Total"],
        "Valor": [f"{consumo} kWh", precio_kwh, cargo_fijo, total]
    })
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📊 Descargar Excel",
        data=output.getvalue(),
        file_name=f"Cobro_{n_cliente}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with c2:
    img_data = crear_imagen_pro(nombre, n_cliente, consumo, total, precio_kwh, cargo_fijo)
    st.download_button(
        label="🖼️ Descargar Imagen PNG",
        data=img_data,
        file_name=f"Boleta_{n_cliente}.png",
        mime="image/png"
    )

# Vista previa de la imagen al final
st.image(img_data, caption="Vista previa de tu boleta digital")
