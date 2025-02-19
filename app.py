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

# JavaScript para copiar al portapapeles
st.markdown("""
<script>
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Error al copiar: ', err);
        return false;
    }
}
</script>
""", unsafe_allow_html=True)

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
            
            for idx, cred in enumerate(results, 1):
                st.markdown(f"""
                <div style='padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin: 10px 0;'>
                    <h3>Resultado #{idx}</h3>
                    <p><strong>URL:</strong> {cred['URL']}</p>
                    <div style='display: flex; align-items: center; margin: 5px 0;'>
                        <strong>Usuario:</strong>
                        <input type='text' value='{cred['Usuario']}' readonly style='margin: 0 10px; padding: 5px; border: 1px solid #ddd;'>
                        <button onclick='copyToClipboard("{cred['Usuario']}")' 
                                style='padding: 5px 10px; background-color: #4CAF50; color: white; border: none; border-radius: 3px; cursor: pointer;'>
                            Copiar
                        </button>
                    </div>
                    <div style='display: flex; align-items: center; margin: 5px 0;'>
                        <strong>Contraseña:</strong>
                        <input type='text' value='{cred['Contraseña']}' readonly style='margin: 0 10px; padding: 5px; border: 1px solid #ddd;'>
                        <button onclick='copyToClipboard("{cred['Contraseña']}")' 
                                style='padding: 5px 10px; background-color: #4CAF50; color: white; border: none; border-radius: 3px; cursor: pointer;'>
                            Copiar
                        </button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No se encontraron coincidencias.")
