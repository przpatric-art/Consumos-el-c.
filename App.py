
import streamlit as st
from st_supabase_connection import SupabaseConnection
from fpdf import FPDF
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Gestión Eléctrica", layout="centered")
conn = st.connection("supabase", type=SupabaseConnection)

# Menú lateral
menu = st.sidebar.selectbox("Seleccione Acción", 
    ["Registrar Lectura", "Generar Boleta", "Agregar Medidor", "Configurar Precios"])

# --- ITEM 4 y 5: CONFIGURACIÓN DE PRECIOS ---
if menu == "Configurar Precios":
    st.header("⚙️ Ajustes de Cobro")
    conf = conn.query("*", table="configuracion").eq("id", 1).execute().data[0]
    
    with st.form("conf_form"):
        kwh = st.number_input("Precio por kWh", value=float(conf['precio_kwh']))
        toma = st.number_input("Cargo por Toma de Lectura", value=float(conf['cargo_lectura']))
        porton = st.number_input("Gasto Portón Total (a dividir)", value=float(conf['cargo_porton_total']))
        if st.form_submit_button("Guardar Cambios"):
            conn.query("*", table="configuracion").upsert({"id":1, "precio_kwh":kwh, "cargo_lectura":toma, "cargo_porton_total":porton}).execute()
            st.success("Precios actualizados")

# --- ITEM 1: AGREGAR MEDIDOR ---
elif menu == "Agregar Medidor":
    st.header("👤 Registro de Medidor")
    with st.form("medidor_form"):
        serie = st.text_input("Número de Serie")
        dueno = st.text_input("Nombre del Dueño")
        ubicacion = st.text_input("Ubicación/Depto")
        tel = st.text_input("WhatsApp (Ej: 56912345678)")
        if st.form_submit_button("Registrar"):
            conn.query("*", table="medidores").insert({"numero_serie":serie, "nombre_dueno":dueno, "nombre_ubicacion":ubicacion, "telefono_contacto":tel}).execute()
            st.success("Registrado con éxito")

# --- ITEM 2: REGISTRAR LECTURA ---
elif menu == "Registrar Lectura":
    st.header("🔌 Toma de Lectura")
    busqueda = st.text_input("Buscar por Serie")
    if busqueda:
        m = conn.query("*", table="medidores").ilike("numero_serie", f"%{busqueda}%").execute().data
        if m:
            st.write(f"Dueño: {m[0]['nombre_dueno']}")
            lectura_val = st.number_input("Lectura Actual (kWh)", min_value=0.0)
            if st.button("Guardar"):
                conn.query("*", table="lecturas").insert({"medidor_id":m[0]['id'], "valor_kwh":lectura_val}).execute()
                st.success("Lectura guardada")

# --- ITEM 3 Y 6: GENERAR BOLETA ---
elif menu == "Generar Boleta":
    st.header("📄 Generar Boleta")
    serie_b = st.text_input("Serie del Medidor")
    if serie_b:
        m = conn.query("*", table="medidores").ilike("numero_serie", f"%{serie_b}%").execute().data
        if m:
            m = m[0]
            conf = conn.query("*", table="configuracion").eq("id", 1).execute().data[0]
            lecs = conn.query("*", table="lecturas").eq("medidor_id", m['id']).order("fecha_lectura", desc=True).limit(2).execute().data
            
            if len(lecs) >= 2:
                cons = lecs[0]['valor_kwh'] - lecs[1]['valor_kwh']
                total_med = conn.query("id", table="medidores", count="exact").execute().count
                p_porton = conf['cargo_porton_total'] / total_med
                p_luz = cons * conf['precio_kwh']
                total = p_luz + conf['cargo_lectura'] + p_porton
                
                texto_boleta = f"DUEÑO: {m['nombre_dueno']}\nConsumo: {cons}kWh\nLuz: ${p_luz:,.2f}\nToma: ${conf['cargo_lectura']}\nPortón: ${p_porton:,.2f}\nTOTAL: ${total:,.2f}"
                st.code(texto_boleta)
                
                # Botón WhatsApp
                msg = urllib.parse.quote(f"Hola {m['nombre_dueno']}, tu cobro de luz es:\n{texto_boleta}")
                st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/{m['telefono_contacto']}?text={msg})")
                
                # Generar PDF
                if st.button("Descargar PDF"):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(0,10, "BOLETA DE CONSUMO", 1, 1, 'C')
                    pdf.set_font("Arial", "", 12)
                    pdf.ln(10)
                    pdf.cell(0,10, f"Dueño: {m['nombre_dueno']}")
                    pdf.ln(10)
                    pdf.cell(0,10, f"Consumo del mes: {cons} kWh")
                    pdf.ln(20)
                    pdf.cell(0,10, f"Total a pagar: ${total:,.2f}")
                    pdf_out = pdf.output(dest='S').encode('latin-1')
                    st.download_button("Click para descargar", pdf_out, "boleta.pdf", "application/pdf")
