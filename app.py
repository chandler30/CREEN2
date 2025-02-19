import streamlit as st
import pandas as pd
import pyperclip  # Para copiar al portapapeles

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

# Función para copiar texto al portapapeles
def copy_to_clipboard(text):
    pyperclip.copy(text)
    st.toast(f"Copiado: {text}")

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

            # Mostrar la tabla con scroll horizontal
            st.dataframe(df, use_container_width=True)

            # Botones de copiar por cada fila
            for index, row in df.iterrows():
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"🔗 {row['URL']}")
                with col2:
                    if st.button(f"📋 Copiar Usuario {index+1}", key=f"user_{index}"):
                        copy_to_clipboard(row["Usuario"])
                with col3:
                    if st.button(f"📋 Copiar Contraseña {index+1}", key=f"pass_{index}"):
                        copy_to_clipboard(row["Contraseña"])
        else:
            st.warning("⚠️ No se encontraron coincidencias.")
