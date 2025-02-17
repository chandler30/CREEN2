import streamlit as st
import os
import re
import rarfile
import zipfile
import shutil
from tempfile import mkdtemp
import time

st.set_page_config(page_title="Buscador de Credenciales", layout="wide")

def procesar_archivo_comprimido(archivo_subido, temp_dir):
    """Procesa un archivo RAR o ZIP y extrae solo los archivos .txt"""
    nombre_archivo = archivo_subido.name
    ruta_archivo = os.path.join(temp_dir, nombre_archivo)
    
    # Guardar el archivo subido
    with open(ruta_archivo, 'wb') as f:
        f.write(archivo_subido.getbuffer())
    
    # Crear directorio para los archivos extraídos
    extracted_dir = os.path.join(temp_dir, 'extracted')
    os.makedirs(extracted_dir, exist_ok=True)
    
    try:
        if nombre_archivo.lower().endswith('.rar'):
            with rarfile.RarFile(ruta_archivo) as rf:
                for file in rf.namelist():
                    if file.lower().endswith('.txt'):
                        rf.extract(file, extracted_dir)
        elif nombre_archivo.lower().endswith('.zip'):
            with zipfile.ZipFile(ruta_archivo) as zf:
                for file in zf.namelist():
                    if file.lower().endswith('.txt'):
                        zf.extract(file, extracted_dir)
    except Exception as e:
        st.error(f"Error al procesar {nombre_archivo}: {str(e)}")
    finally:
        # Eliminar el archivo comprimido original
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
    
    return extracted_dir

def buscar_credenciales(directorio, texto_url):
    """Busca credenciales en archivos .txt basándose en coincidencias de URL"""
    resultados = []
    patrones = {
        'url': [
            r"URL:\s*(.*?)\s*$",
            r"URL\s*:\s*(.*?)\s*$",
            r"URL\s+(.*?)\s*$"
        ],
        'usuario': [
            r"USER:\s*(.*?)\s*$",
            r"USERNAME:\s*(.*?)\s*$",
            r"Usuario:\s*(.*?)\s*$",
            r"USER\s*:\s*(.*?)\s*$"
        ],
        'password': [
            r"PASS:\s*(.*?)\s*$",
            r"PASSWORD:\s*(.*?)\s*$",
            r"Contraseña:\s*(.*?)\s*$",
            r"PASS\s*:\s*(.*?)\s*$"
        ]
    }
    
    patrones_compilados = {
        tipo: [re.compile(p, re.IGNORECASE) for p in patterns]
        for tipo, patterns in patrones.items()
    }

    def encontrar_coincidencia(linea, tipo_patron):
        for patron in patrones_compilados[tipo_patron]:
            coincidencia = patron.search(linea)
            if coincidencia:
                return coincidencia.group(1)
        return None

    for root, _, files in os.walk(directorio):
        for file in files:
            if file.endswith('.txt'):
                ruta_archivo = os.path.join(root, file)
                try:
                    with open(ruta_archivo, 'r', encoding='utf-8') as f:
                        lineas = f.readlines()
                    
                    i = 0
                    while i < len(lineas):
                        url = encontrar_coincidencia(lineas[i], 'url')
                        if url and texto_url.lower() in url.lower():
                            usuario = None
                            password = None
                            
                            # Buscar credenciales en las siguientes líneas
                            for j in range(i, min(i + 5, len(lineas))):
                                if not usuario:
                                    usuario = encontrar_coincidencia(lineas[j], 'usuario')
                                if not password:
                                    password = encontrar_coincidencia(lineas[j], 'password')
                            
                            if usuario and password:
                                resultados.append({
                                    "archivo": file,
                                    "url": url,
                                    "usuario": usuario,
                                    "password": password
                                })
                        i += 1
                        
                except Exception as e:
                    st.warning(f"Error al procesar {file}: {str(e)}")
    
    return resultados

def main():
    st.title("🔍 Buscador de Credenciales")
    
    # Crear directorio temporal
    temp_dir = mkdtemp()
    
    st.write("### 📤 Subir Archivos")
    archivos = st.file_uploader(
        "Arrastra aquí tus archivos RAR o ZIP", 
        type=['rar', 'zip'],
        accept_multiple_files=True
    )
    
    texto_busqueda = st.text_input("🔎 Ingresa el texto a buscar en las URLs (ej: google.com):")
    
    if archivos and texto_busqueda:
        with st.spinner("Procesando archivos..."):
            for archivo in archivos:
                extracted_dir = procesar_archivo_comprimido(archivo, temp_dir)
                resultados = buscar_credenciales(extracted_dir, texto_busqueda)
                
                if resultados:
                    st.success(f"Se encontraron {len(resultados)} coincidencias en {archivo.name}")
                    
                    # Mostrar resultados en una tabla expandible
                    with st.expander(f"Ver resultados de {archivo.name}"):
                        for resultado in resultados:
                            st.markdown("""---""")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write("**Archivo:**", resultado['archivo'])
                            with col2:
                                st.write("**URL:**", resultado['url'])
                            with col3:
                                st.write("**Usuario:**", resultado['usuario'])
                                st.write("**Contraseña:**", resultado['password'])
                else:
                    st.info(f"No se encontraron coincidencias en {archivo.name}")
            
            # Limpiar archivos temporales
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                st.error(f"Error al limpiar archivos temporales: {str(e)}")

if __name__ == "__main__":
    main()
