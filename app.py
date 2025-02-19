import streamlit as st
import pandas as pd

# Configuración de la aplicación - DEBE SER LA PRIMERA LLAMADA A STREAMLIT
st.set_page_config(page_title="Buscador de Credenciales", layout="wide")

def parse_lines(lines):
    data = []
    for line in lines:
        line = line.strip()
        if ";" in line:
            parts = line.split(";")
        elif "|" in line:
            parts = line.split("|")
        else:
            continue
        if len(parts) == 3:
            url, user, password = parts
            data.append({"URL": url, "Usuario": user, "Contraseña": password})
    return data

# Función mejorada para generar un botón de copiar con JavaScript y CSS responsive
def copy_button(text, label):
    return f"""
    <button onclick="navigator.clipboard.writeText('{text}')"
    style="background-color: #4CAF50; 
           color: white; 
           border: none; 
           padding: 5px 10px; 
           border-radius: 4px;
           cursor: pointer; 
           font-size: 12px; 
           margin: 2px 0;
           white-space: nowrap;
           display: inline-block;">
        📋 {label}
    </button>
    """

# CSS personalizado para mejorar la responsividad
st.markdown("""
<style>
    .credential-box {
        border: 1px solid #ddd;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        background-color: white;
        word-wrap: break-word;
    }
    .credential-item {
        margin: 5px 0;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
    }
    .credential-label {
        font-weight: bold;
        margin-right: 5px;
        white-space: nowrap;
    }
    .credential-value {
        word-break: break-all;
        flex: 1;
        min-width: 150px;
    }
    @media (max-width: 640px) {
        .credential-item {
            flex-direction: column;
            align-items: flex-start;
        }
        .credential-value {
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Buscador de Credenciales en TXT")

# Subir archivo .txt
uploaded_file = st.file_uploader("📂 Sube un archivo .txt con las credenciales", type="txt")

if uploaded_file:
    # Leer y procesar el archivo
    content = uploaded_file.read().decode("utf-8").split("\n")
    credentials = parse_lines(content)
    
    # Entrada para buscar URL
    search_url = st.text_input("🔗 Ingresa la URL a buscar:")
    
    if search_url:
        # Filtrar coincidencias
        results = [cred for cred in credentials if search_url.lower() in cred["URL"].lower()]
        
        if results:
            st.success(f"✅ Se encontraron {len(results)} coincidencias:")
            
            # Mostrar cada resultado en un contenedor responsive
            for cred in results:
                st.markdown(f"""
                    <div class="credential-box">
                        <div class="credential-item">
                            <span class="credential-label">🔗 URL:</span>
                            <span class="credential-value">{cred["URL"]}</span>
                        </div>
                        <div class="credential-item">
                            <span class="credential-label">👤 Usuario:</span>
                            <span class="credential-value">{cred["Usuario"]}</span>
                            {copy_button(cred["Usuario"], "Copiar")}
                        </div>
                        <div class="credential-item">
                            <span class="credential-label">🔑 Contraseña:</span>
                            <span class="credential-value">{cred["Contraseña"]}</span>
                            {copy_button(cred["Contraseña"], "Copiar")}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No se encontraron coincidencias.")
