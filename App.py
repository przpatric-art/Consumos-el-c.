import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
import datetime

# Función para formato moneda chilena
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(page_title="Generador de Boletas Eléctricas", page_icon="⚡")

st.title("⚡ Cobro Eléctrico Digital")

# --- ENTRADA DE DATOS (SIDEBAR) ---
with st.sidebar:
    st.header("Datos del Cliente")
    nombre = st.text_input("Nombre del Cliente", "Juan Pérez")
    n_cliente = st.text_input("N° de Cliente", "123456")
    
    st.header("Consumo y Cargos")
    ant = st.number_input("Lectura Anterior (kWh)", min_value=0)
    actual = st.number_input("Lectura Actual (kWh)", min_value=0)
    precio_kwh = st.number_input("Precio por kWh ($)", min_value=0.0, value=150.0)
    cargo_fijo = st.number_input("Cargo Toma Lectura ($)", min_value=0, value=1000)
    cobros_extras = st.number_input("Otros Cobros / Extras ($)", min_value=0, value=0)

# --- CÁLCULOS ---
consumo_mes = max(0, actual - ant)
subtotal_consumo = round(consumo_mes * precio_kwh)
total_final = subtotal_consumo + cargo_fijo + cobros_extras

# --- RESUMEN EN PANTALLA ---
st.subheader("Resumen del Cobro")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Consumo", f"{consumo_mes} kWh")
c2.metric("Valor kWh", format_clp(precio_kwh))
c3.metric("Extras", format_clp(cobros_extras))
c4.metric("TOTAL", format_clp(total_final))

# --- FUNCIÓN PARA GENERAR IMAGEN ---
def crear_imagen_boleta(nombre, n_cliente, consumo, v_kwh, cargo_fijo, extras, total):
    ancho, alto = 500, 600
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Encabezado azul oscuro
    draw.rectangle([0, 0, ancho, 80], fill=(20, 40, 60))
    draw.text((30, 25), "BOLETA DE COBRO ELÉCTRICO", fill=(255, 255, 255))
    
    # Datos Cliente
    y = 110
    draw.text((40, y), f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}", fill=(0, 0, 0))
    draw.text((40, y+30), f"Cliente: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, y+60), f"N. Cuenta: {n_cliente}", fill=(0, 0, 0))
    
    draw.line([40, 210, 460, 210], fill=(200, 200, 200), width=1)
    
    # Detalle con Valor kWh incluido
    y_det = 230
    draw.text((40, y_det), "DETALLE DE COBROS", fill=(20, 40, 60))
    
    draw.text((40, y_det+40), f"Consumo Mes: {consumo} kWh", fill=(50, 50, 50))
    draw.text((40, y_det+70), f"Valor por kWh:", fill=(50, 50, 50))
    draw.text((320, y_det+70), format_clp(v_kwh), fill=(0, 0, 0))
    
    draw.text((40, y_det+100), f"Subtotal Consumo:", fill=(50, 50, 50))
    draw.text((320, y_det+100), format_clp(round(consumo * v_kwh)), fill=(0, 0, 0))
    
    draw.text((40, y_det+130), "Cargo Toma Lectura:", fill=(50, 50, 50))
    draw.text((320, y_det+130), format_clp(cargo_fijo), fill=(0, 0, 0))
    
    draw.text((40, y_det+160), "Cobros Extras / Otros:", fill=(50, 50, 50))
    draw.text((320, y_det+160), format_clp(extras), fill=(0, 0, 0))
    
    # Recuadro Total
    draw.rectangle([40, 430, 460, 500], outline=(20, 40, 60), width=2)
    draw.text((60, 455), "TOTAL A PAGAR", fill=(20, 40, 60))
    draw.text((320, 455), f"{format_clp(total)}", fill=(0, 0, 0))
    
    draw.text((130, 540), "Gracias por su pago puntual", fill=(150, 150, 150))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- BOTONES ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    img_data = crear_imagen_boleta(nombre, n_cliente, consumo_mes, precio_kwh, cargo_fijo, cobros_extras, total_final)
    st.download_button("🖼️ Descargar Imagen PNG", img_data, f"Boleta_{n_cliente}.png", "image/png")

with col2:
    df_ex = pd.DataFrame({"Item": ["Lectura Ant", "Lectura Act", "Consumo", "Valor kWh", "Extras", "Total"], 
                          "Valor": [ant, actual, consumo_mes, precio_kwh, cobros_extras, total_final]})
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_ex.to_excel(writer, index=False)
    st.download_button("📊 Descargar Excel", output.getvalue(), f"Reporte_{n_cliente}.xlsx")

st.image(img_data, caption="Vista previa de la boleta")
