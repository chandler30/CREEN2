import streamlit as st
import pyperclip

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
            
            # Mostrar resultados con botones de copiar
            for idx, cred in enumerate(results, 1):
                st.markdown(f"### Resultado #{idx}")
                st.write(f"**URL:** {cred['URL']}")
                
                # Usuario con botón de copiar
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Usuario:** {cred['Usuario']}")
                with col2:
                    if st.button(f"Copiar Usuario #{idx}"):
                        st.session_state[f'copy_user_{idx}'] = True
                        pyperclip.copy(cred['Usuario'])
                        st.success("¡Usuario copiado!")
                
                # Contraseña con botón de copiar
                col3, col4 = st.columns([3, 1])
                with col3:
                    st.write(f"**Contraseña:** {cred['Contraseña']}")
                with col4:
                    if st.button(f"Copiar Contraseña #{idx}"):
                        st.session_state[f'copy_pass_{idx}'] = True
                        pyperclip.copy(cred['Contraseña'])
                        st.success("¡Contraseña copiada!")
                
                st.markdown("---")
        else:
            st.warning("No se encontraron coincidencias.")
