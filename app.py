import streamlit as st
import pandas as pd

# Función para parsear las líneas del archivo
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

# Función para generar un botón de copiar con JavaScript
def copy_button(text, label):
    return f"""
    <button onclick="navigator.clipboard.writeText('{text}')" 
    style="background-color: #4CAF50; color: white; border: none; padding: 5px 10px; 
    cursor: pointer; font-size: 14px; margin-left: 10px;">
        📋 {label}
    </button>
    """

# Configuración de la aplicación
st.set_page_config(page_title="Buscador de Credenciales", layout="wide")
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
        results = [cred for cred in credentials if search_url in cred["URL"]]

        if results:
            st.success(f"✅ Se encontraron {len(results)} coincidencias:")

            # Convertir a DataFrame para mostrar en tabla interactiva
            df = pd.DataFrame(results)

            # Mostrar la tabla con botones de copiar
            for index, row in df.iterrows():
                st.markdown(
                    f"""
                    <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 5px; border-radius: 5px;">
                        <strong>🔗 URL:</strong> {row["URL"]}<br>
                        <strong>👤 Usuario:</strong> {row["Usuario"]} {copy_button(row["Usuario"], "Copiar Usuario")}<br>
                        <strong>🔑 Contraseña:</strong> {row["Contraseña"]} {copy_button(row["Contraseña"], "Copiar Contraseña")}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("⚠️ No se encontraron coincidencias.")
