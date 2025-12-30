import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
import datetime

# Función para formato moneda chilena (Punto para miles)
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(page_title="Generador de Boletas Simplificadas", page_icon="⚡")

st.title("⚡ Generador de Cobro Eléctrico")

# --- ENTRADA DE DATOS (SIDEBAR) ---
with st.sidebar:
    st.header("👤 Datos del Cliente")
    nombre = st.text_input("Nombre del Cliente", "Juan Pérez")
    n_cliente = st.text_input("N° de Cliente", "123456")
    
    st.header("⚙️ Parámetros de Cálculo (Internos)")
    st.info("Estos valores se usan para el total, pero NO aparecerán en la boleta.")
    precio_kwh = st.number_input("Valor por kWh ($)", min_value=0.0, value=150.0)
    cobro_general = st.number_input("Cobro General / Base ($)", min_value=0, value=0)
    
    st.header("📊 Consumo y Extras")
    ant = st.number_input("Lectura Anterior (kWh)", min_value=0)
    actual = st.number_input("Lectura Actual (kWh)", min_value=0)
    cargo_lectura = st.number_input("Cargo Toma Lectura ($)", min_value=0, value=1000)
    cobros_extras = st.number_input("Otros Cobros Extras ($)", min_value=0, value=0)

# --- LÓGICA DE CÁLCULO ---
consumo_mes = max(0, actual - ant)
# El total suma: (Consumo * Precio) + Cargo Lectura + Cobro General + Extras
monto_consumo_calculado = round(consumo_mes * precio_kwh)
total_final = monto_consumo_calculado + cargo_lectura + cobro_general + cobros_extras

# --- RESUMEN EN PANTALLA ---
st.subheader("Resumen de Liquidación")
c1, c2, c3 = st.columns(3)
c1.metric("Consumo Mes", f"{consumo_mes} kWh")
c2.metric("Extras Registrados", format_clp(cobros_extras))
c3.metric("TOTAL A PAGAR", format_clp(total_final))

# --- FUNCIÓN PARA GENERAR IMAGEN (BOLETA LIMPIA) ---
def crear_imagen_limpia(nombre, n_cliente, consumo, cargo_lec, extras, total):
    ancho, alto = 500, 500
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Encabezado Minimalista
    draw.rectangle([0, 0, ancho, 7
