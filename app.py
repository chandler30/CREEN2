import streamlit as st

def parse_lines(lines):
    """Parsea las líneas del archivo y devuelve una lista de diccionarios con URL, usuario y contraseña."""
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

# Configuración de la aplicación
st.title("Buscador de credenciales en TXT")

# Subir archivo .txt
uploaded_file = st.file_uploader("Sube un archivo .txt con las credenciales", type="txt")

if uploaded_file:
    # Leer y procesar el archivo
    content = uploaded_file.read().decode("utf-8").split("\n")
    credentials = parse_lines(content)

    # Entrada para buscar URL
    search_url = st.text_input("Ingresa la URL a buscar:")

    if search_url:
        # Filtrar coincidencias
        results = [cred for cred in credentials if search_url in cred["URL"]]

        if results:
            st.success(f"Se encontraron {len(results)} coincidencias:")
            st.table(results)
        else:
            st.warning("No se encontraron coincidencias.")
