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

def create_table_html(results):
    html = """
    <style>
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .custom-table tr {
            border-bottom: 1px solid #f0f0f0;
        }
        .custom-table tr:last-child {
            border-bottom: none;
        }
        .custom-table td {
            padding: 12px;
            vertical-align: middle;
        }
        .custom-table .url-cell {
            word-break: break-all;
            color: #1a73e8;
        }
        .custom-table .copy-button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 8px;
            white-space: nowrap;
        }
        .credential-value {
            font-family: monospace;
            background-color: #f8f9fa;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }
        @media (max-width: 640px) {
            .custom-table td {
                display: block;
                padding: 8px 12px;
            }
            .custom-table td:before {
                content: attr(data-label);
                font-weight: bold;
                display: block;
                margin-bottom: 4px;
            }
            .credential-value {
                display: inline-block;
                margin-right: 8px;
            }
        }
    </style>
    """
    
    for cred in results:
        html += f"""
        <table class="custom-table">
            <tr>
                <td data-label="URL" class="url-cell">{cred["URL"]}</td>
            </tr>
            <tr>
                <td data-label="Usuario">
                    <span class="credential-value">{cred["Usuario"]}</span>
                    <button class="copy-button" onclick="navigator.clipboard.writeText('{cred["Usuario"]}')" >
                        📋 Copiar Usuario
                    </button>
                </td>
            </tr>
            <tr>
                <td data-label="Contraseña">
                    <span class="credential-value">{cred["Contraseña"]}</span>
                    <button class="copy-button" onclick="navigator.clipboard.writeText('{cred["Contraseña"]}')" >
                        📋 Copiar Contraseña
                    </button>
                </td>
            </tr>
        </table>
        <div style="height: 16px"></div>
        """
    return html

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
            
            # Mostrar resultados usando la nueva función de tabla HTML
            st.markdown(create_table_html(results), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No se encontraron coincidencias.")
