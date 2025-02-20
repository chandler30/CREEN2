import streamlit as st
import pandas as pd

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

def save_to_txt(credentials, filename="resultados.txt"):
    with open(filename, "w") as file:
        for cred in credentials:
            file.write(f"{cred['Usuario']}:{cred['Contraseña']}\n")

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
            if len(results) > 100:
                save_to_txt(results)
                st.success(f"Se encontraron {len(results)} coincidencias. Las coincidencias se han guardado en un archivo .txt.")
                st.download_button(label="Descargar resultados", data=open("resultados.txt", "rb"), file_name="resultados.txt", mime="text/plain")
            else:
                st.success(f"Se encontraron {len(results)} coincidencias:")
                
                for idx, cred in enumerate(results, 1):
                    st.markdown(f"### Resultado #{idx}")
                    st.write(f"**URL:** {cred['URL']}")
                    
                    # Contenedor para usuario
                    st.write("**Usuario:**")
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.text_input("", value=cred['Usuario'], key=f"user_{idx}", disabled=True)
                    with col2:
                        if st.button("📋 Copiar", key=f"copy_user_{idx}"):
                            st.write("Usuario copiado! 👇")
                            st.code(cred['Usuario'])
                    
                    # Contenedor para contraseña
                    st.write("**Contraseña:**")
                    col3, col4 = st.columns([3,1])
                    with col3:
                        st.text_input("", value=cred['Contraseña'], key=f"pass_{idx}", disabled=True)
                    with col4:
                        if st.button("📋 Copiar", key=f"copy_pass_{idx}"):
                            st.write("Contraseña copiada! 👇")
                            st.code(cred['Contraseña'])
                    
                    st.markdown("---")
        else:
            st.warning("No se encontraron coincidencias.")
