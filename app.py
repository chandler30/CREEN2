import streamlit as st

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
            
            # Estilos para hacer la tabla más amigable en móviles
            st.markdown("""
            <style>
                .result-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .result-table th, .result-table td {
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                    font-size: 14px;
                }
                .copy-btn {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    margin-left: 10px;
                    cursor: pointer;
                    font-size: 12px;
                }
                .copy-btn:hover {
                    background-color: #45a049;
                }
                @media screen and (max-width: 600px) {
                    .result-table th, .result-table td {
                        font-size: 12px;
                        padding: 8px;
                    }
                    .copy-btn {
                        font-size: 10px;
                        padding: 4px 8px;
                    }
                }
            </style>
            """, unsafe_allow_html=True)

            # Mostrar tabla con botones de copiar
            table_html = "<table class='result-table'><tr><th>🔗 URL</th><th>👤 Usuario</th><th>🔑 Contraseña</th></tr>"
            for cred in results:
                table_html += f"""
                <tr>
                    <td>{cred['URL']}</td>
                    <td>
                        {cred['Usuario']}
                        <button class='copy-btn' onclick="navigator.clipboard.writeText('{cred['Usuario']}')">📋 Copiar</button>
                    </td>
                    <td>
                        {cred['Contraseña']}
                        <button class='copy-btn' onclick="navigator.clipboard.writeText('{cred['Contraseña']}')">📋 Copiar</button>
                    </td>
                </tr>
                """
            table_html += "</table>"

            st.markdown(table_html, unsafe_allow_html=True)

        else:
            st.warning("⚠️ No se encontraron coincidencias.")
