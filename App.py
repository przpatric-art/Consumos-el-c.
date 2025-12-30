import streamlit as st
from fpdf import FPDF
import datetime

# Configuración de la página
st.set_page_config(page_title="Calculadora Eléctrica", page_icon="⚡")

st.title("⚡ Calculadora de Consumo Eléctrico")
st.markdown("Complete los datos para generar su liquidación de consumo.")

# --- SECCIÓN 1: Datos del Cliente ---
st.header("1. Información del Cliente")
col1, col2 = st.columns(2)
with col1:
    nombre_cliente = st.text_input("Nombre completo")
with col2:
    numero_cliente = st.text_input("Número de cliente")

# --- SECCIÓN 2: Lecturas y Costos ---
st.header("2. Detalles de Consumo")
c1, c2, c3 = st.columns(3)
with c1:
    valor_anterior = st.number_input("Lectura Anterior (kWh)", min_value=0.0, step=1.0)
with c2:
    valor_actual = st.number_input("Lectura Actual (kWh)", min_value=0.0, step=1.0)
with c3:
    valor_kwh = st.number_input("Valor por kWh ($)", min_value=0.0, step=0.1)

cargo_lectura = st.number_input("Valor cobro por toma de lectura ($)", min_value=0.0, step=1.0)

# --- SECCIÓN 3: Cálculos ---
consumo_total = max(0.0, valor_actual - valor_anterior)
subtotal_consumo = consumo_total * valor_kwh
total_pagar = subtotal_consumo + cargo_lectura

st.divider()
st.subheader(f"Total a Pagar: ${total_pagar:,.2f}")

# --- SECCIÓN 4: Generación de PDF ---
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Boleta de Consumo Eléctrico", ln=True, align='C')
    
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Fecha: {datetime.date.today()}", ln=True)
    pdf.cell(200, 10, f"Cliente: {nombre_cliente}", ln=True)
    pdf.cell(200, 10, f"N° Cliente: {numero_cliente}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, f"Lectura Anterior: {valor_anterior} kWh", ln=True)
    pdf.cell(200, 10, f"Lectura Actual: {valor_actual} kWh", ln=True)
    pdf.cell(200, 10, f"Consumo Total: {consumo_total} kWh", ln=True)
    pdf.cell(200, 10, f"Valor kWh: ${valor_kwh}", ln=True)
    pdf.cell(200, 10, f"Cargo toma de lectura: ${cargo_lectura}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"TOTAL A PAGAR: ${total_pagar:,.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

if st.button("Generar Boleta para Descarga"):
    if nombre_cliente and numero_cliente:
        pdf_bytes = generar_pdf()
        st.download_button(
            label="⬇️ Descargar Boleta (PDF)",
            data=pdf_bytes,
            file_name=f"Boleta_{numero_cliente}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Por favor, ingrese los datos del cliente antes de descargar.")
