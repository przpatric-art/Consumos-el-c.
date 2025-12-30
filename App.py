import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
import datetime

# Función para formato moneda chilena
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(page_title="Generador de Boletas", page_icon="⚡")

st.title("⚡ Generador de Cobro Eléctrico")

# --- ENTRADA DE DATOS (SIDEBAR) ---
with st.sidebar:
    st.header("👤 Datos del Cliente")
    nombre = st.text_input("Nombre del Cliente", "Juan Pérez")
    n_cliente = st.text_input("N° de Cliente", "123456")
    
    st.header("⚙️ Parámetros Internos (Ocultos)")
    # Estos dos NO aparecerán en la boleta
    precio_kwh = st.number_input("Valor por kWh ($)", min_value=0.0, value=150.0)
    cobro_general_base = st.number_input("Cobro General Editable ($)", min_value=0, value=0)
    
    st.header("📊 Datos de Consumo y Visibles")
    ant = st.number_input("Lectura Anterior (kWh)", min_value=0)
    actual = st.number_input("Lectura Actual (kWh)", min_value=0)
    cargo_lectura = st.number_input("Cargo Toma Lectura ($)", min_value=0, value=1000)
    cobros_extras = st.number_input("Otros Cobros Extras ($)", min_value=0, value=0)

# --- LÓGICA DE CÁLCULO (Todo suma al total) ---
consumo_mes = max(0, actual - ant)
monto_por_consumo = round(consumo_mes * precio_kwh)

# El Total suma todo, incluyendo los ítems que pediste ocultar
total_final = monto_por_consumo + cobro_general_base + cargo_lectura + cobros_extras

# --- FUNCIÓN PARA GENERAR IMAGEN (BOLETA MODIFICADA) ---
def crear_boleta_limpia(nombre, n_cliente, consumo, cargo_lec, extras, total):
    ancho, alto = 500, 500
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Encabezado
    draw.rectangle([0, 0, ancho, 80], fill=(30, 30, 30))
    draw.text((30, 30), "COMPROBANTE DE COBRO ELÉCTRICO", fill=(255, 255, 255))
    
    # Datos Cliente
    y = 110
    fecha = datetime.date.today().strftime('%d/%m/%Y')
    draw.text((40, y), f"Fecha: {fecha}", fill=(0, 0, 0))
    draw.text((40, y+30), f"Cliente: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, y+60), f"N. Cuenta: {n_cliente}", fill=(0, 0, 0))
    
    draw.line([40, 200, 460, 200], fill=(200, 200, 200), width=1)
    
    # DETALLE VISIBLE
    y_det = 230
    draw.text((40, y_det), "DETALLE DE LA CUENTA", fill=(100, 100, 100))
    
    # Solo mostramos el consumo como texto, no su valor monetario ni el valor kWh
    draw.text((40, y_det+40), f"Consumo registrado en el mes:", fill=(0, 0, 0))
    draw.text((350, y_det+40), f"{consumo} kWh", fill=(0, 0, 0))
    
    # Solo mostramos cargos fijos y extras
    draw.text((40, y_det+70), "Cargo Toma de Lectura:", fill=(0, 0, 0))
    draw.text((350, y_det+70), format_clp(cargo_lec), fill=(0, 0, 0))
    
    if extras > 0:
        draw.text((40, y_det+100), "Cobros Adicionales:", fill=(0, 0, 0))
        draw.text((350, y_det+100), format_clp(extras), fill=(0, 0, 0))
    
    # TOTAL (Este valor ya incluye el cobro general y el valor kwh internamente)
    draw.rectangle([40, 380, 460, 450], outline=(0, 0, 0), width=2)
    draw.text((60, 405), "TOTAL NETO A PAGAR", fill=(0, 0, 0))
    draw.text((350, 405), f"{format_clp(total)}", fill=(0, 0, 0))
    
    draw.text((150, 470), "Gracias por su pago", fill=(150, 150, 150))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- INTERFAZ DE DESCARGA ---
st.divider()
img_final = crear_boleta_limpia(nombre, n_cliente, consumo_mes, cargo_lectura, cobros_extras, total_final)

col1, col2 = st.columns(2)
with col1:
    st.download_button("🖼️ Descargar Imagen para WhatsApp", img_final, f"Boleta_{n_cliente}.png", "image/png")
with col2:
    # El Excel sí guarda todo para tu respaldo
    df_respaldo = pd.DataFrame({
        "Detalle": ["Consumo kWh", "Precio kWh (Oculto)", "Cobro General (Oculto)", "Cargo Lectura", "Extras", "Total Pago"],
        "Valor": [consumo_mes, precio_kwh, cobro_general_base, cargo_lectura, cobros_extras, total_final]
    })
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_respaldo.to_excel(writer, index=False)
    st.download_button("📊 Descargar Excel Interno", output.getvalue(), f"Control_{n_cliente}.xlsx")

st.image(img_final, caption="Vista previa de la boleta (El Valor kWh y Cobro General están sumados en el total pero no aparecen aquí)")
