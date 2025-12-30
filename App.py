import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# Configuración
st.set_page_config(page_title="Calculadora Eléctrica Chile", page_icon="⚡")

def format_chilean_pesos(valor):
    return f"${int(valor):,}".replace(",", ".")

st.title("⚡ Generador de Cobro Eléctrico")

# --- ENTRADA DE DATOS ---
with st.expander("📝 Datos del Cliente y Consumo", expanded=True):
    nombre = st.text_input("Nombre del Cliente")
    n_cliente = st.text_input("Número de Cliente")
    
    col1, col2 = st.columns(2)
    with col1:
        ant = st.number_input("Lectura Anterior (kWh)", min_value=0.0)
        actual = st.number_input("Lectura Actual (kWh)", min_value=0.0)
    with col2:
        precio_kwh = st.number_input("Valor kWh ($ CLP)", min_value=0.0, format="%.2f")
        cargo_fijo = st.number_input("Cargo Toma Lectura ($ CLP)", min_value=0)

# --- CÁLCULOS ---
consumo = max(0.0, actual - ant)
subtotal = round(consumo * precio_kwh)
total = subtotal + int(cargo_fijo)

# Crear un DataFrame para mostrar y exportar
datos_boleta = {
    "Concepto": ["Lectura Anterior", "Lectura Actual", "Consumo Mes", "Valor kWh", "Cargo Lectura", "TOTAL A PAGAR"],
    "Detalle": [f"{ant} kWh", f"{actual} kWh", f"{consumo} kWh", f"${precio_kwh}", format_chilean_pesos(cargo_fijo), format_chilean_pesos(total)]
}
df = pd.DataFrame(datos_boleta)

st.subheader("Resumen de Cobro")
st.table(df)

# --- EXPORTAR A EXCEL ---
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Boleta')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# --- EXPORTAR A IMAGEN ---
# Creamos una representación visual simple para la "Captura"
def generar_recuadro_imagen():
    # Streamlit no puede "tomar fotos" de sí mismo fácilmente, 
    # pero podemos crear un bloque de texto formateado que el usuario puede capturar
    # o usar un componente para descargar el resumen.
    st.info("💡 Consejo: Para enviar por RRSS, puedes tomar una captura de pantalla al recuadro de arriba o descargar el Excel.")

# --- BOTONES DE DESCARGA ---
st.divider()
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    excel_data = to_excel(df)
    st.download_button(
        label="📥 Descargar Excel",
        data=excel_data,
        file_name=f"Cobro_{n_cliente}_{nombre}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col_btn2:
    if st.button("📸 Generar Formato Imagen"):
        st.write("---")
        st.markdown(f"""
        ### 🧾 COMPROBANTE DE COBRO
        **Cliente:** {nombre}  
        **N° Cuenta:** {n_cliente}  
        **Fecha:** {datetime.date.today().strftime('%d/%m/%Y')}
        
        * Consumo: {consumo} kWh
        * Valor kWh: ${precio_kwh}
        * Cargo Lectura: {format_chilean_pesos(cargo_fijo)}
        
        **TOTAL A PAGAR: {format_chilean_pesos(total)}**
        ---
        """)
        st.caption("Puedes sacar una captura de pantalla (Screenshot) a este recuadro para enviarlo por WhatsApp.")

