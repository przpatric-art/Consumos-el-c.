import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import datetime
import random

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Generador de Boletas ⚡", page_icon="⚡", layout="centered")

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

# --- LÓGICA DE NEGOCIO ---
consumo_mes = actual - ant
if consumo_mes < 0:
    st.error("⚠️ Error: La lectura actual no puede ser menor a la anterior.")
    consumo_mes = 0

monto_energia = round(consumo_mes * precio_kwh)
total_final = monto_energia + cargo
