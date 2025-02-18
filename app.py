import streamlit as st
import os
import re
import zipfile
import shutil
from tempfile import mkdtemp
import subprocess
import glob
from time import sleep

st.set_page_config(page_title="Buscador de Credenciales", layout="wide")

def extraer_rar(ruta_rar, directorio_destino, password=None):
    """Extrae un archivo RAR usando unrar-free o unrar con contraseña"""
    try:
        if password:
            result = subprocess.run(['unrar', 'x', '-p' + password, ruta_rar, directorio_destino], 
                          check=True, 
                          capture_output=True)
        else:
            result = subprocess.run(['unrar-free', 'x', ruta_rar, directorio_destino], 
                          check=True, 
                          capture_output=True)
        return True, result
    except subprocess.CalledProcessError as e:
        st.error(f"Error al extraer RAR: {e}")
        return False, e
    except Exception as e:
        st.error(f"Error inesperado: {e}")
        return False, e

def procesar_archivo_comprimido(temp_file_path, temp_dir, password=None):
    """Procesa un archivo RAR o ZIP y extrae solo los archivos .txt"""
    nombre_archivo = os.path.basename(temp_file_path)
    
    try:
        # Crear directorio para los archivos extraídos
        extracted_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extracted_dir, exist_ok=True)
        
        # Procesar según el tipo de archivo
        if nombre_archivo.lower().endswith('.rar'):
            # Crear un subdirectorio temporal para la extracción RAR
            rar_temp_dir = os.path.join(temp_dir, 'rar_temp')
            os.makedirs(rar_temp_dir, exist_ok=True)
            
            # Extraer el RAR
            success, result = extraer_rar(temp_file_path, rar_temp_dir, password)
            if success:
                # Copiar solo los archivos .txt al directorio final
                for txt_file in glob.glob(os.path.join(rar_temp_dir, '**/*.txt'), recursive=True):
                    shutil.copy2(txt_file, extracted_dir)
                # Limpiar directorio temporal RAR
                shutil.rmtree(rar_temp_dir)
            
        elif nombre_archivo.lower().endswith('.zip'):
            with zipfile.ZipFile(temp_file_path) as zf:
                for file in zf.namelist():
                    if file.lower().endswith('.txt'):
                        zf.extract(file, extracted_dir)
        
        # Contar archivos .txt extraídos
        txt_files_count = len(glob.glob(os.path.join(extracted_dir, '**/*.txt'), recursive=True))
        st.write(f"Se encontraron {txt_files_count} archivos .txt en {nombre_archivo}")
        
        return extracted_dir
        
    except Exception as e:
        st.error(f"Error al procesar {nombre_archivo}: {str(e)}")
        return None

def buscar_credenciales_por_url(ruta_carpeta, texto_url):
    """
    Busca credenciales en archivos .txt basándose en coincidencias parciales de URL.

    Args:
        ruta_carpeta (str): Ruta del directorio con los archivos .txt
        texto_url (str): Texto a buscar en las URLs (coincidencia parcial)
    """

    resultados = []
    # Patrones más flexibles para diferentes formatos
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

    # Compilar todos los patrones
    patrones_compilados = {
        tipo: [re.compile(p, re.IGNORECASE) for p in patterns]
        for tipo, patterns in patrones.items()
    }

    def encontrar_coincidencia(linea, tipo_patron):
        """Busca coincidencias con cualquiera de los patrones del tipo especificado"""
        for patron in patrones_compilados[tipo_patron]:
            coincidencia = patron.search(linea)
            if coincidencia:
                return coincidencia.group(1)
        return None

    # Verificar si la carpeta existe
    if not os.path.exists(ruta_carpeta):
        print(f"Error: La carpeta {ruta_carpeta} no existe.")
        return

    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".txt"):
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    lineas = f.readlines()

                i = 0
                while i < len(lineas):
                    # Buscar URL
                    url = encontrar_coincidencia(lineas[i], 'url')
                    if url and texto_url.lower() in url.lower():
                        # Buscar credenciales en las siguientes líneas
                        usuario = None
                        password = None
                        for j in range(i, min(i + 5, len(lineas))):  # Buscar en las próximas 5 líneas
                            if not usuario:
                                usuario = encontrar_coincidencia(lineas[j], 'usuario')
                            if not password:
                                password = encontrar_coincidencia(lineas[j], 'password')

                        if usuario and password:
                            resultados.append({
                                "archivo": archivo,
                                "url": url,
                                "usuario": usuario,
                                "password": password
                            })
                    i += 1

            except Exception as e:
                print(f"Error al procesar el archivo {archivo}: {e}")

    # Mostrar resultados en Streamlit
    if resultados:
        st.write(f"\nSe encontraron {len(resultados)} coincidencias para '{texto_url}':")
        for resultado in resultados:
            st.markdown("\n" + "="*50)
            st.write(f"Archivo: {resultado['archivo']}")
            st.write(f"URL: {resultado['url']}")
            st.write(f"Usuario: {resultado['usuario']}")
            st.write(f"Contraseña: {resultado['password']}")
    else:
        st.write(f"\nNo se encontraron credenciales para '{texto_url}' en la carpeta {ruta_carpeta}")

def main():
    st.title("🔍 Buscador de Credenciales")
    
    # Crear directorio temporal
    temp_dir = mkdtemp()
    
    st.write("### 📤 Subir Archivos")
    st.write("Sube archivos RAR o ZIP que contengan archivos .txt")
    
    archivos = st.file_uploader(
        "Arrastra aquí tus archivos", 
        type=['rar', 'zip'],
        accept_multiple_files=False
    )
    
    texto_busqueda = st.text_input("🔎 Ingresa el texto a buscar en las URLs (ej: google.com):")
    password_rar = st.text_input("🔑 Ingresa la contraseña para archivos RAR (si aplica):", type="password")
    
    extracted_dir = None  # Initialize extracted_dir here
    
    if archivos:
        st.write("### 🛠️ Opciones de Procesamiento")
        if st.button('Descomprimir Temporalmente'):
            with st.spinner("Descomprimiendo archivo..."):
                temp_file_path = os.path.join(temp_dir, archivos.name)
                with open(temp_file_path, 'wb') as f:
                    f.write(archivos.getvalue())
                
                progress_bar = st.progress(0)
                for i in range(100):
                    sleep(0.1)  # Simulate work being done
                    progress_bar.progress(i + 1)
                
                success, result = extraer_rar(temp_file_path, temp_dir, password_rar)
                if success:
                    st.success("Archivo descomprimido exitosamente.")
                    extracted_dir = temp_dir
                else:
                    st.error(f"Error al descomprimir el archivo: {result}")
        
        if extracted_dir and st.button('Extraer .txt'):
            with st.spinner("Extrayendo archivos .txt..."):
                txt_dir = procesar_archivo_comprimido(temp_file_path, temp_dir, password_rar)
                if txt_dir:
                    st.success("Archivos .txt extraídos exitosamente.")
                    
    if texto_busqueda and extracted_dir:
        total_resultados = 0
        
        with st.spinner("Buscando credenciales..."):
            buscar_credenciales_por_url(os.path.join(temp_dir, 'extracted'), texto_busqueda)

if __name__ == "__main__":
    main()
