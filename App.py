import streamlit as st
from st_supabase_connection import SupabaseConnection
from fpdf import FPDF
import urllib.parse
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Cobro Eléctrico", layout="centered")

# 2. CONEXIÓN A SUPABASE
# Esta línea busca los datos en Settings > Secrets de Streamlit Cloud
try:
    conn = st.connection("supabase", type=SupabaseConnection)
except Exception as e:
    st.error("Error de conexión. Revisa los 'Secrets' en Streamlit Cloud.")
    st.stop()

# 3. MENÚ LATERAL
st.sidebar.title("Menú Principal")
menu = st.sidebar.selectbox("Seleccione una opción:", 
    ["Registrar Lectura", "Generar Boleta", "Agregar Medidor", "Configurar Precios"])

# --- ITEM: CONFIGURAR PRECIOS (Factor kWh y Portón) ---
if menu == "Configurar Precios":
    st.header("⚙️ Configuración de Cobros")
    
    # Obtener valores actuales de la base de datos
    conf_query = conn.query("*", table="configuracion").eq("id", 1).execute()
    actual = conf_query.data[0] if conf_query.data else {"precio_kwh": 0.0, "cargo_lectura": 0.0, "cargo_porton_total": 0.0}

    with st.form("form_config"):
        nuevo_kwh = st.number_input("Precio por kWh", value=float(actual['precio_kwh']), format="%.2f")
        nuevo_toma = st.number_input("Cobro por toma de lectura", value=float(actual['cargo_lectura']), format="%.2f")
        nuevo_porton = st.number_input("Gasto Portón Total (a repartir)", value=float(actual['cargo_porton_total']), format="%.2f")
        
        if st.form_submit_button("Actualizar Precios"):
            conn.query("*", table="configuracion").upsert({
                "id": 1, 
                "precio_kwh": nuevo_kwh, 
                "cargo_lectura": nuevo_toma, 
                "cargo_porton_total": nuevo_porton
            }).execute()
            st.success("✅ Precios actualizados correctamente")

# --- ITEM: AGREGAR MEDIDOR (Dueño y Datos) ---
elif menu == "Agregar Medidor":
    st.header("👤 Registro de Nuevo Medidor")
    with st.form("form_medidor"):
        serie = st.text_input("Número de Serie del Medidor")
        dueno = st.text_input("Nombre del Dueño")
        ubicacion = st.text_input("Ubicación (Ej: Depto 101)")
        tel = st.text_input("WhatsApp (Ej: 56912345678)")
        
        if st.form_submit_button("Guardar Medidor"):
            if serie and dueno:
                conn.query("*", table="medidores").insert({
                    "numero_serie": serie, 
                    "nombre_dueno": dueno, 
                    "nombre_ubicacion": ubicacion,
                    "telefono_contacto": tel
                }).execute()
                st.success(f"✅ Medidor {serie} de {dueno} registrado")
            else:
                st.error("Por favor llena los campos obligatorios")

# --- ITEM: REGISTRAR LECTURA ---
elif menu == "Registrar Lectura":
    st.header("🔌 Toma de Lectura")
    busqueda = st.text_input("Buscar medidor por Serie")
    if busqueda:
        res = conn.query("*", table="medidores").ilike("numero_serie", f"%{busqueda}%").execute()
        if res.data:
            m = res.data[0]
            st.info(f"Dueño: {m['nombre_dueno']} | Ubicación: {m['nombre_ubicacion']}")
            lectura_val = st.number_input("Ingrese Lectura Actual (kWh)", min_value=0.0)
            if st.button("Guardar Lectura"):
                conn.query("*", table="lecturas").insert({
                    "medidor_id": m['id'], 
                    "valor_kwh": lectura_val
                }).execute()
                st.success("✅ Lectura guardada")
        else:
            st.warning("Medidor no encontrado")

# --- ITEM: GENERAR BOLETA (PDF y WhatsApp) ---
elif menu == "Generar Boleta":
    st.header("📄 Generar Boleta de Cobro")
    serie_b = st.text_input("Serie del Medidor para Facturar")
    
    if serie_b:
        res = conn.query("*", table="medidores").ilike("numero_serie", f"%{serie_b}%").execute()
        if res.data:
            m = res.data[0]
            conf = conn.query("*", table="configuracion").eq("id", 1).execute().data[0]
            
            # Obtener las últimas 2 lecturas para calcular consumo
            lecs = conn.query("*", table="lecturas").eq("medidor_id", m['id']).order("fecha_lectura", desc=True).limit(2).execute().data
            
            if len(lecs) >= 2:
                actual = lecs[0]['valor_kwh']
                anterior = lecs[1]['valor_kwh']
                consumo = actual - anterior
                
                # Cálculos
                total_medidores = conn.query("id", table="medidores", count="exact").execute().count
                cuota_porton = conf['cargo_porton_total'] / total_medidores if total_medidores > 0 else 0
                pago_energia = consumo * conf['precio_kwh']
                total_final = pago_energia + conf['cargo_lectura'] + cuota_porton
                
                # Mostrar Resumen
                resumen = f"""
                DUEÑO: {m['nombre_dueno']}
                MEDIDOR: {m['numero_serie']}
                --------------------------
                Consumo: {consumo} kWh
                Energía: ${pago_energia:,.2f}
                Toma Lectura: ${conf['cargo_lectura']:,.2f}
                Portón/Extra: ${cuota_porton:,.2f}
                --------------------------
                TOTAL: ${total_final:,.2f}
                """
                st.code(resumen)
                
                # Botón WhatsApp
                msg = urllib.parse.quote(f"Hola {m['nombre_dueno']}, tu cobro de luz es:\n{resumen}")
                st.markdown(f"[📲 Enviar por WhatsApp a {m['nombre_dueno']}](https://wa.me/{m['telefono_contacto']}?text={msg})")
                
                # Generar PDF
                if st.button("Descargar PDF"):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(0, 10, "BOLETA DE CONSUMO ELÉCTRICO", 0, 1, 'C')
                    pdf.ln(10)
                    pdf.set_font("Arial", "", 12)
                    pdf.cell(0, 10, f"Dueño: {m['nombre_dueno']}")
                    pdf.ln(8)
                    pdf.cell(0, 10, f"Medidor: {m['numero_serie']}")
                    pdf.ln(15)
                    pdf.cell(0, 10, f"Consumo: {consumo} kWh")
                    pdf.ln(8)
                    pdf.cell(0, 10, f"Monto Energía: ${pago_energia:,.2f}")
                    pdf.ln(8)
                    pdf.cell(0, 10, f"Toma de Lectura: ${conf['cargo_lectura']:,.2f}")
                    pdf.ln(8)
                    pdf.cell(0, 10, f"Cargo Portón: ${cuota_porton:,.2f}")
                    pdf.ln(15)
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, f"TOTAL A PAGAR: ${total_final:,.2f}")
                    
                    pdf_output = pdf.output(dest='S').encode('latin-1')
                    st.download_button("📥 Click para descargar PDF", pdf_output, "boleta.pdf", "application/pdf")
            else:
                st.warning("Se necesitan al menos 2 lecturas registradas para calcular el consumo.")
