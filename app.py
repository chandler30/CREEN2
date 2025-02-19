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
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        console.log('Texto copiado');
    }).catch(function(err) {
        console.error('Error al copiar texto: ', err);
    });
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
            
            # Mostrar resultados con botones de copiar
            for idx, cred in enumerate(results):
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;">
                    <p><strong>URL:</strong> {cred['URL']}</p>
                    <p>
                        <strong>Usuario:</strong> {cred['Usuario']}
                        <button 
                            onclick="copyToClipboard('{cred['Usuario']}')"
                            style="margin-left: 10px; padding: 2px 8px; cursor: pointer;">
                            Copiar
                        </button>
                    </p>
                    <p>
                        <strong>Contraseña:</strong> {cred['Contraseña']}
                        <button 
                            onclick="copyToClipboard('{cred['Contraseña']}')"
                            style="margin-left: 10px; padding: 2px 8px; cursor: pointer;">
                            Copiar
                        </button>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No se encontraron coincidencias.")
