import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
import datetime

# Función para formato moneda chilena (sin decimales, puntos en miles)
def format_clp(valor):
    return f"${int(valor):,}".replace(",", ".")

st.set_page_config(page_title="Generador de Boletas Eléctricas", page_icon="⚡")

# --- MENÚ LATERAL (SIDEBAR) ---
st.sidebar.header("📋 DATOS DEL CLIENTE")
nombre = st.sidebar.text_input("Nombre y Apellido", "Juan Pérez")
n_cliente = st.sidebar.text_input("Número de Cliente", "001")

st.sidebar.header("💰 VALORES DE CÁLCULO (INTERNOS)")
# Estos ítems NO aparecen en la boleta
precio_kwh = st.sidebar.number_input("1. Editar Valor por kWh ($)", min_value=0.0, value=150.0)
cobro_general = st.sidebar.number_input("2. Editar Cobro General ($)", min_value=0, value=0)

st.sidebar.header("📝 ITEMS DE LA BOLETA (VISIBLES)")
# Estos ítems SÍ aparecen en la boleta
ant = st.sidebar.number_input("Lectura Anterior (kWh)", min_value=0)
actual = st.sidebar.number_input("Lectura Actual (kWh)", min_value=0)
cargo_lectura = st.sidebar.number_input("Valor Toma de Lectura ($)", min_value=0, value=1000)
cobro_porton_camara = st.sidebar.number_input("Cobro por Portón y Cámara ($)", min_value=0, value=0)

# --- LÓGICA DE CÁLCULO ---
consumo_mes = max(0, actual - ant)
subtotal_energia = round(consumo_mes * precio_kwh)
total_final = subtotal_energia + cobro_general + cargo_lectura + cobro_porton_camara

# --- INTERFAZ PRINCIPAL ---
st.title("⚡ Generador de Boleta Eléctrico")

st.subheader("Resumen de Cobro Actual")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Consumo", f"{consumo_mes} kWh")
c2.metric("Portón/Cámara", format_clp(cobro_porton_camara))
c3.metric("C. General", format_clp(cobro_general))
c4.metric("TOTAL FINAL", format_clp(total_final))

# --- GENERACIÓN DE IMAGEN (LA BOLETA PROFESIONAL AZUL) ---
def generar_imagen_final():
    # Dimensiones de la boleta
    ancho, alto = 500, 550
    # Color de fondo (Blanco)
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. ENCABEZADO (Azul Profesional)
    azul_oscuro = (26, 54, 104) # Color Corporativo
    draw.rectangle([0, 0, ancho, 100], fill=azul_oscuro)
    draw.text((30, 40), "BOLETA DE COBRO ELÉCTRICO", fill=(255, 255, 255))
    
    # 2. DATOS DEL CLIENTE Y FECHA
    y = 130
    fecha_hoy = datetime.date.today().strftime('%d/%m/%Y')
    draw.text((40, y), f"Fecha de Emisión: {fecha_hoy}", fill=(50, 50, 50))
    draw.text((40, y+30), f"CLIENTE: {nombre.upper()}", fill=(0, 0, 0))
    draw.text((40, y+60), f"N. CUENTA: {n_cliente}", fill=(0, 0, 0))
    
    # Línea divisoria azul clara
    draw.line([40, 230, 460, 230], fill=(200, 200, 200), width=1)
    
    # 3. DETALLE DE CONSUMO Y SERVICIOS
    y_det = 250
    draw.text((40, y_det), "DETALLE DE CONSUMO Y SERVICIOS", fill=azul_oscuro)
    
    # Consumo
    draw.text((40, y_det+40), "Consumo registrado en el mes:", fill=(50, 50, 50))
    draw.text((350, y_det+40), f"{consumo_mes} kWh", fill=(0, 0, 0))
    
    # Toma de lectura
    draw.text((40, y_det+70), "Cargo Toma de Lectura:", fill=(50, 50, 50))
    draw.text((350, y_det+70), format_clp(cargo_lectura), fill=(0, 0, 0))
    
    # Portón y Cámara (Sólo si es mayor a 0)
    if cobro_porton_camara > 0:
        draw.text((40, y_det+100), "Cobro Portón y Cámara:", fill=(50, 50, 50))
        draw.text((350, y_det+100), format_clp(cobro_porton_camara), fill=(0, 0, 0))
    
    # 4. RECUADRO DE TOTAL (Estilo resaltado)
    # Dibujamos un fondo azul muy suave para el total
    draw.rectangle([30, 410, 470, 480], outline=azul_oscuro, width=2)
    draw.text((50, 435), "TOTAL A PAGAR", fill=azul_oscuro)
    draw.text((350, 435), f"{format_clp(total_final)}", fill=(0, 0, 0))
    
    # Pie de página
    draw.text((140, 510), "Gracias por su pago puntual.", fill=(150, 150, 150))

    # Guardar en buffer
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- BOTONES DE DESCARGA ---
st.divider()
img_boleta = generar_imagen_final()

col_img, col_xl = st.columns(2)
with col_img:
    st.download_button(
        label="🖼️ Descargar Imagen PNG",
        data=img_boleta,
        file_name=f"Boleta_{n_cliente}.png",
        mime="image/png"
    )
with col_xl:
    # Excel para registro interno
    df = pd.DataFrame({
        "Concepto": ["Consumo kWh", "Precio kWh (Oculto)", "Cobro General (Oculto)", "Cargo Lectura", "Porton y Camara", "Total Final"],
        "Monto": [consumo_mes, precio_kwh, cobro_general, cargo_lectura, cobro_porton_camara, total_final]
    })
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button(
        label="📊 Descargar Excel Interno",
        data=output.getvalue(),
        file_name=f"Control_Interno_{n_cliente}.xlsx"
    )

# Previsualización
st.image(img_boleta, caption="Vista previa de la boleta profesional")
