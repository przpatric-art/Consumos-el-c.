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
    precio_kwh = st.number_input("Precio kWh ($)", min_value=0.0, value=150.0) # Se usa para el cálculo interno
    cargo_fijo = st.number_input("Cargo Toma Lectura ($)", min_value=0, value=1000)
    cobros_extras = st.number_input("Otros Cobros / Extras ($)", min_value=0, value=0)

# --- CÁLCULOS INTERNOS ---
consumo_mes = max(0, actual - ant)
subtotal_consumo = round(consumo_mes * precio_kwh)
total_final = subtotal_consumo + cargo_fijo + cobros_extras

# --- RESUMEN EN PANTALLA ---
st.subheader("Resumen del Cobro")
c1, c2, c3 = st.columns(3)
c1.metric("Consumo Mes", f"{consumo_mes} kWh")
c2.metric("Cobros Extras", format_clp(cobros_extras))
c3.metric("TOTAL A PAGAR", format_clp(total_final))

# --- FUNCIÓN PARA GENERAR IMAGEN ESTILIZADA ---
def crear_imagen_boleta(nombre, n_cliente, consumo, cargo_fijo, extras, total):
    # Crear lienzo (Ancho x Alto)
    ancho, alto = 500, 550
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Encabezado
    draw.rectangle([0, 0, ancho, 80], fill=(20, 40, 60))
    draw.text((30, 25), "BOLETA DE COBRO ELÉCTRICO", fill=(255, 255, 255))
    
    # Datos Cliente
    y = 110
    draw.text((40, y), f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}", fill=(0, 0, 0))
    draw.text((40, y+30), f"Cliente: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, y+60), f"N. Cuenta: {n_cliente}", fill=(0, 0, 0))
    
    # Línea decorativa
    draw.line([40, 210, 460, 210], fill=(200, 200, 200), width=1)
    
    # Detalle de Cobros (Sin valor kWh)
    y_det = 230
    draw.text((40, y_det), "DETALLE DE COBROS", fill=(20, 40, 60))
    
    draw.text((40, y_det+40), f"Consumo del Mes ({consumo} kWh):", fill=(50, 50, 50))
    draw.text((320, y_det+40), format_clp(round(consumo * precio_kwh)), fill=(0, 0, 0))
    
    draw.text((40, y_det+70), "Cargo Toma Lectura:", fill=(50, 50, 50))
    draw.text((320, y_det+70), format_clp(cargo_fijo), fill=(0, 0, 0))
    
    draw.text((40, y_det+100), "Cobros Extras / Otros:", fill=(50, 50, 50))
    draw.text((320, y_det+100), format_clp(extras), fill=(0, 0, 0))
    
    # Recuadro Total
    draw.rectangle([40, 370, 460, 440], outline=(20, 40, 60), width=2)
    draw.text((60, 395), "TOTAL A PAGAR", fill=(20, 40, 60))
    draw.text((320, 395), f"{format_clp(total)}", fill=(0, 0, 0))
    
    draw.text((130, 490), "Gracias por su pago puntual", fill=(150, 150, 150))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- ACCIONES DE DESCARGA ---
st.divider()
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    # Generar Excel Actualizado
    df_excel = pd.DataFrame({
        "Concepto": ["Consumo (kWh)", "Monto Consumo", "Cargo Lectura", "Cobros Extras", "TOTAL"],
        "Valor": [consumo_mes, format_clp(subtotal_consumo), format_clp(cargo_fijo), format_clp(cobros_extras), format_clp(total_final)]
    })
    output_ex = BytesIO()
    with pd.ExcelWriter(output_ex, engine='openpyxl') as writer:
        df_excel.to_excel(writer, index=False, sheet_name='Boleta')
    
    st.download_button(
        label="📥 Descargar Registro Excel",
        data=output_ex.getvalue(),
        file_name=f"Cobro_{n_cliente}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col_btn2:
    # Generar Imagen Pro
    img_data = crear_imagen_boleta(nombre, n_cliente, consumo_mes, cargo_fijo, cobros_extras, total_final)
    st.download_button(
        label="🖼️ Descargar Imagen para WhatsApp",
        data=img_data,
        file_name=f"Boleta_{n_cliente}.png",
        mime="image/png"
    )

# Vista previa final
st.image(img_data, caption="Vista previa de la boleta generada")
