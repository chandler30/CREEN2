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

# Componente para manejar el copiado
def create_copy_button(text, button_label="Copiar"):
    button_id = f"copy_button_{hash(text)}"
    return f'''
        <div style="display: inline-block;">
            <span>{text}</span>
            <button 
                id="{button_id}"
                onclick="
                    navigator.clipboard.writeText('{text}');
                    document.getElementById('{button_id}').innerText='¡Copiado!';
                    setTimeout(() => document.getElementById('{button_id}').innerText='Copiar', 1000)
                "
                style="margin-left: 10px; padding: 2px 8px; cursor: pointer; background-color: #4CAF50; color: white; border: none; border-radius: 3px;">
                {button_label}
            </button>
        </div>
    '''

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
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; background-color: #f9f9f9;">
                    <h3 style="margin-top: 0; color: #333;">Resultado #{idx}</h3>
                    <p><strong>URL:</strong> {cred['URL']}</p>
                    <p>
                        <strong>Usuario:</strong> {create_copy_button(cred['Usuario'])}
                    </p>
                    <p>
                        <strong>Contraseña:</strong> {create_copy_button(cred['Contraseña'])}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No se encontraron coincidencias.")
