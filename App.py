import streamlit as st
from st_supabase_connection import SupabaseConnection
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title="Cobro Eléctrico Inmediato", layout="centered")

# Conexión Segura
try:
    conn = st.connection("supabase", type=SupabaseConnection)
except Exception as e:
    st.error("Error de configuración en Secrets. Revisa las llaves.")
    st.stop()

menu = st.sidebar.selectbox("Menú", ["Generar Boleta Inmediata", "Configurar Precios", "Administrar Medidores"])

# --- CONFIGURACIÓN DE PRECIOS ---
if menu == "Configurar Precios":
    st.header("⚙️ Ajustes de Cobro")
    res = conn.query("*", table="configuracion").eq("id", 1).execute()
    actual = res.data[0] if res.data else {"precio_kwh": 0, "cargo_lectura": 0, "cargo_porton_total": 0}
    
    with st.form("conf"):
        kwh = st.number_input("Precio kWh", value=float(actual['precio_kwh']))
        toma = st.number_input("Cargo Toma Lectura", value=float(actual['cargo_lectura']))
        porton = st.number_input("Gasto Portón Total", value=float(actual['cargo_porton_total']))
        if st.form_submit_button("Guardar"):
            conn.query("*", table="configuracion").upsert({"id":1, "precio_kwh":kwh, "cargo_lectura":toma, "cargo_porton_total":porton}).execute()
            st.success("Precios guardados")

# --- GENERAR BOLETA (CÁLCULO INMEDIATO) ---
elif menu == "Generar Boleta Inmediata":
    st.header("📄 Nueva Boleta")
    
    # 1. Seleccionar Medidor
    medidores_res = conn.query("numero_serie, nombre_dueno, telefono_contacto", table="medidores").execute()
    opciones = {f"{m['numero_serie']} - {m['nombre_dueno']}": m for m in medidores_res.data}
    
    seleccion = st.selectbox("Seleccione Medidor", ["Seleccione..."] + list(opciones.keys()))
    
    if seleccion != "Seleccione...":
        m = opciones[seleccion]
        conf = conn.query("*", table="configuracion").eq("id", 1).execute().data[0]
        
        col1, col2 = st.columns(2)
        with col1:
            ant = st.number_input("Lectura ANTERIOR", min_value=0.0)
        with col2:
            act = st.number_input("Lectura ACTUAL", min_value=0.0)
            
        if act < ant:
            st.warning("La lectura actual no puede ser menor a la anterior.")
        else:
            consumo = act - ant
            
            # Cálculo de Portón (Total / cantidad de medidores)
            total_m = len(medidores_res.data)
            p_porton = conf['cargo_porton_total'] / total_m if total_m > 0 else 0
            p_luz = consumo * conf['precio_kwh']
            total = p_luz + conf['cargo_lectura'] + p_porton
            
            # Resultado Visual
            st.subheader("Resumen de Cobro")
            resumen = f"""
            DUEÑO: {m['nombre_dueno']}
            CONSUMO: {consumo} kWh
            ------------------------
            Energía: ${p_luz:,.2f}
            Toma de Lectura: ${conf['cargo_lectura']:,.2f}
            Cuota Portón: ${p_porton:,.2f}
            ------------------------
            TOTAL A PAGAR: ${total:,.2f}
            """
            st.info(resumen)
            
            # WhatsApp
            msg = urllib.parse.quote(f"Estimado {m['nombre_dueno']}, su cobro de luz es:\n{resumen}")
            st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/{m['telefono_contacto']}?text={msg})")
            
            # Botón para Guardar en Base de Datos (Opcional)
            if st.button("💾 Registrar esta lectura en el historial"):
                conn.query("*", table="lecturas").insert({"medidor_id": conn.query("id", table="medidores").eq("numero_serie", m['numero_serie']).execute().data[0]['id'], "valor_kwh": act}).execute()
                st.success("Historial actualizado.")

# --- ADMINISTRAR MEDIDORES ---
elif menu == "Administrar Medidores":
    st.header("🔌 Registro de Medidores")
    with st.form("add_m"):
        s = st.text_input("N° Serie")
        d = st.text_input("Dueño")
        t = st.text_input("Teléfono (Ej: 56912345678)")
        if st.form_submit_button("Agregar"):
            conn.query("*", table="medidores").insert({"numero_serie":s, "nombre_dueno":d, "telefono_contacto":t}).execute()
            st.rerun()
