import streamlit as st
import pandas as pd

# ==========================================
# 1. Configuración de la página
# ==========================================
st.set_page_config(
    page_title="Buscador de Materiales", 
    page_icon="🔍", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. Inicializar la "Memoria" (Session State)
# ==========================================
if 'vista' not in st.session_state:
    st.session_state.vista = 'buscador'
if 'item_seleccionado' not in st.session_state:
    st.session_state.item_seleccionado = None
if 'busqueda_guardada' not in st.session_state:
    st.session_state.busqueda_guardada = ""

# ==========================================
# 3. Estilos CSS
# ==========================================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 1rem; padding-bottom: 5rem;}
    * { font-family: 'Roboto', sans-serif; }

    div[data-baseweb="input"] {
        border-radius: 8px !important;
        border: 1px solid #e0e0e0 !important;
        background-color: white !important;
    }
    
    /* ESTILOS EXCLUSIVOS PARA LAS TARJETAS */
    button[title="tarjeta"] {
        width: 100% !important;
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        margin-bottom: 8px !important;
        padding: 16px !important;
        display: block !important;
        height: auto !important;
        white-space: normal !important;
    }
    button[title="tarjeta"]:hover {
        border-color: #1a73e8 !important;
        box-shadow: 0 4px 8px rgba(26,115,232,0.15) !important;
        color: inherit !important;
    }
    button[title="tarjeta"] > div {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
    }
    button[title="tarjeta"] p {
        text-align: left !important;
        margin-bottom: 4px !important;
        font-size: 15px !important;
        color: #1f2937 !important;
        line-height: 1.5 !important;
        width: 100% !important;
    }

    /* ESTILO PARA EL BOTÓN DE LIMPIAR (X) */
    button[title="Limpiar búsqueda"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #5f6368 !important;
        font-size: 20px !important;
        padding: 4px !important;
        margin-top: -2px !important;
    }
    button[title="Limpiar búsqueda"]:hover {
        color: #d93025 !important;
        background-color: transparent !important;
    }

    /* UI Fija */
    .bottom-nav {
        position: fixed; bottom: 0; left: 0; width: 100%; background-color: white;
        display: flex; justify-content: space-around; padding: 10px 0;
        border-top: 1px solid #e0e0e0; z-index: 1000;
    }
    .nav-item { display: flex; flex-direction: column; align-items: center; text-decoration: none; color: #5f6368; font-size: 12px; }
    .nav-item.active { color: #1a73e8; font-weight: bold; }
    .nav-icon { font-size: 24px; margin-bottom: 4px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. Función para cargar el Excel
# ==========================================
@st.cache_data
def cargar_datos():
    try:
        # Aseguramos forzosamente que lea Data_Limpia
        df = pd.read_excel('datos_ejemplo.xlsx', sheet_name='Data_Limpia')
        # Limpiamos espacios al inicio y final de los nombres de columnas
        df.columns = df.columns.str.strip() 
        df = df.fillna("") 
        return df
    except Exception as e:
        st.error(f"⚠️ Error al cargar el archivo: {e}")
        return pd.DataFrame()

df = cargar_datos()

if not df.empty:
    
    # ==========================================
    # VISTA 1: EL BUSCADOR PRINCIPAL
    # ==========================================
    if st.session_state.vista == 'buscador':
        
        st.write("") 
        
        # Título principal agregado
        st.markdown('<h2 style="color: #1a73e8; text-align: center; margin-bottom: 20px;">Repuestos Área eléctrica SECA</h2>', unsafe_allow_html=True)
        
        # Nueva estructura de columnas sin el ícono de menú
        col1, col2 = st.columns([8, 1])
        with col1:
            # Placeholder actualizado
            busqueda = st.text_input("Buscar", value=st.session_state.busqueda_guardada, placeholder="Ingresar palabra clave o numero de material", label_visibility="collapsed")
            st.session_state.busqueda_guardada = busqueda
        with col2:
            if st.button("✕", help="Limpiar búsqueda"):
                st.session_state.busqueda_guardada = ""
                st.rerun()
        
        st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

        if st.session_state.busqueda_guardada:
            busqueda_lower = st.session_state.busqueda_guardada.lower()
            
            # --- LÓGICA DE BÚSQUEDA MULTI-PALABRA (AND) ---
            # 1. Separar lo que el usuario escribió por espacios
            palabras = busqueda_lower.split()
            
            # 2. Unimos todos los datos de cada fila en un solo bloque de texto en minúsculas
            texto_filas = df.astype(str).apply(lambda x: ' '.join(x).lower(), axis=1)
            
            # 3. Empezamos asumiendo que todas las filas son válidas
            mascara = pd.Series([True] * len(df), index=df.index)
            
            # 4. Filtramos: la fila sobrevive SOLO si contiene TODAS las palabras clave
            for palabra in palabras:
                mascara = mascara & texto_filas.str.contains(palabra)
            
            resultados = df[mascara]
            # ----------------------------------------------

            if not resultados.empty:
                for idx, row in resultados.iterrows():
                    
                    # Búsqueda estrictamente por el nombre de la columna en Data_Limpia
                    col_a = str(row.get("Nombre del archivo", "Sin Archivo")).strip()
                    col_b = str(row.get("Número de material", "Sin Material")).strip()
                    
                    col_d = str(row.get("Nombre técnico (Denominación)", "")).strip()
                    if col_d == "" or col_d.lower() in ["nan", "none", "<na>"]:
                        col_d = " "

                    # Etiqueta de la tarjeta con la estructura solicitada para el Buscador
                    label_tarjeta = f"**⚡ {col_a}**  \n**🔢 {col_b}**  \n🛠️ {col_d}"
                    
                    if st.button(label_tarjeta, key=f"btn_{idx}", help="tarjeta", type="secondary", use_container_width=True):
                        st.session_state.item_seleccionado = row
                        st.session_state.vista = 'detalle'
                        st.rerun()
                        
            else:
                st.warning("No se encontraron resultados.")
        
        # Texto de soporte al final del buscador
        st.markdown("<div style='text-align: center; margin-top: 40px; font-size: 12px; color: #757575;'>Soporte: Anderson Berna C.</div>", unsafe_allow_html=True)

    # ==========================================
    # VISTA 2: LOS DETALLES DE LA TARJETA
    # ==========================================
    elif st.session_state.vista == 'detalle':
        
        if st.button("⬅️ Volver al Buscador", type="primary"):
            st.session_state.vista = 'buscador'
            st.session_state.item_seleccionado = None
            st.rerun()

        item = st.session_state.item_seleccionado

        st.markdown('<h3 style="color: #1a73e8;">Ficha del Material</h3><hr style="margin-top: 0; border-top: 1px solid #e0e0e0;">', unsafe_allow_html=True)

        html_detalles = '<div style="background-color: white; padding: 24px; border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">'
        
        # EL ORDEN EXACTO REQUERIDO
        columnas_ordenadas = [
            "Nombre del archivo",
            "Número de material",
            "Nombre técnico (Denominación)",
            "Tipo de planificación",
            "Descripción textual"
        ]

        # Iteramos y extraemos usando un buscador flexible para evitar problemas de tildes o espacios ocultos
        for titulo in columnas_ordenadas:
            val = ""
            
            # Normalizamos el título que estamos buscando
            titulo_norm = titulo.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').strip()
            
            for col in item.index:
                # Normalizamos el nombre de la columna que viene del Excel
                col_norm = str(col).lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').strip()
                
                # Si los nombres son idénticos o si ambos contienen la palabra clave "planificaci"
                if titulo_norm == col_norm or ("planificaci" in titulo_norm and "planificaci" in col_norm):
                    val = str(item[col]).strip()
                    break
            
            # Limpiar nulos residuales
            if val.lower() in ["nan", "none", "<na>"]:
                val = ""
                
            html_detalles += f'<div style="font-size: 13px; color: #757575; margin-top: 15px; font-weight: bold;">{titulo}</div>'
            html_detalles += f'<div style="font-size: 16px; font-weight: 500; color: #202124; margin-bottom: 5px; min-height: 20px;">{val}</div>'
            html_detalles += '<hr style="margin: 5px 0; border-top: 1px dashed #f0f0f0;">'

        html_detalles += '</div>'
        
        st.markdown(html_detalles, unsafe_allow_html=True)

    # ==========================================
    # ELEMENTOS DE UI FIJOS (NavBar)
    # ==========================================
    st.markdown("""
        <div class="bottom-nav">
            <a href="#" class="nav-item active">
                <span class="nav-icon">📋</span>
                Datos
            </a>
            <a href="#" class="nav-item">
                <span class="nav-icon">📊</span>
                Statistics
            </a>
        </div>
    """, unsafe_allow_html=True)