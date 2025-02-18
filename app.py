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
    """Extrae un archivo RAR usando unrar"""
    try:
        command = ['unrar', 'x']
        if password:
            command.append(f'-p{password}')
        command.extend([ruta_rar, directorio_destino])
        
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        return True, result
    except subprocess.CalledProcessError as e:
        return False, f"Error al extraer RAR: {str(e)}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

def copiar_archivos_passwords(directorio_origen, directorio_destino):
    """
    Copia archivos específicos de contraseñas a un directorio numerado
    """
    # Lista de nombres de archivo a buscar
    archivos_objetivo = ['password.txt', 'passwords.txt', 'PASSWORDS.txt', 'Passwords.txt']
    
    # Crear directorio de destino numerado
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)
    else:
        i = 1
        while os.path.exists(f"{directorio_destino}{i}"):
            i += 1
        directorio_destino = f"{directorio_destino}{i}"
        os.makedirs(directorio_destino)
    
    # Contador para archivos encontrados
    archivos_encontrados = 0
    
    # Recorrer el directorio de origen
    for root, _, files in os.walk(directorio_origen):
        for filename in files:
            if filename.lower() in [f.lower() for f in archivos_objetivo]:
                ruta_origen = os.path.join(root, filename)
                nuevo_nombre = f"password{archivos_encontrados + 1}.txt"
                ruta_destino = os.path.join(directorio_destino, nuevo_nombre)
                
                try:
                    shutil.copy2(ruta_origen, ruta_destino)
                    archivos_encontrados += 1
                except Exception as e:
                    st.error(f"Error al copiar {filename}: {str(e)}")
    
    return archivos_encontrados, directorio_destino

def procesar_archivo_comprimido(temp_file_path, temp_dir, password=None):
    """Procesa un archivo RAR o ZIP y extrae los archivos de contraseñas"""
    nombre_archivo = os.path.basename(temp_file_path)
    
    try:
        # Crear directorio para extracción inicial
        extracted_dir = os.path.join(temp_dir, 'extracted')
        passwords_dir = os.path.join(temp_dir, 'PASSWORD')
        os.makedirs(extracted_dir, exist_ok=True)
        
        # Procesar según el tipo de archivo
        if nombre_archivo.lower().endswith('.rar'):
            success, result = extraer_rar(temp_file_path, extracted_dir, password)
            if not success:
                st.error(result)
                return None
        elif nombre_archivo.lower().endswith('.zip'):
            with zipfile.ZipFile(temp_file_path) as zf:
                zf.extractall(extracted_dir)
        
        # Copiar archivos de contraseñas
        num_archivos, dir_final = copiar_archivos_passwords(extracted_dir, passwords_dir)
        
        if num_archivos > 0:
            st.success(f"Se encontraron y copiaron {num_archivos} archivos de contraseñas")
            return dir_final
        else:
            st.warning("No se encontraron archivos de contraseñas")
            return None
        
    except Exception as e:
        st.error(f"Error al procesar {nombre_archivo}: {str(e)}")
        return None

def buscar_credenciales_por_url(ruta_carpeta, texto_url):
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

    if not os.path.exists(ruta_carpeta):
        st.error(f"La carpeta {ruta_carpeta} no existe.")
        return

    for archivo in os.listdir(ruta_carpeta):
        if archivo.lower().endswith(".txt"):
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            try:
                with open(ruta_archivo, "r", encoding="utf-8", errors='ignore') as f:
                    lineas = f.readlines()

                i = 0
                while i < len(lineas):
                    url = encontrar_coincidencia(lineas[i], 'url')
                    if url and texto_url.lower() in url.lower():
                        usuario = None
                        password = None
                        for j in range(i, min(i + 5, len(lineas))):
                            if not usuario:
                                usuario = encontrar_coincidencia(lineas[j], 'usuario')
                            if not password:
                                password = encontrar_coincidencia(lineas[j], 'password')

                        if usuario or password:
                            resultados.append({
                                "archivo": archivo,
                                "url": url,
                                "usuario": usuario or "No encontrado",
                                "password": password or "No encontrado"
                            })
                    i += 1

            except Exception as e:
                st.error(f"Error al procesar {archivo}: {str(e)}")

    if resultados:
        st.write(f"\nSe encontraron {len(resultados)} coincidencias para '{texto_url}':")
        for resultado in resultados:
            st.markdown("---")
            st.write(f"📄 Archivo: {resultado['archivo']}")
            st.write(f"🔗 URL: {resultado['url']}")
            st.write(f"👤 Usuario: {resultado['usuario']}")
            st.write(f"🔑 Contraseña: {resultado['password']}")
    else:
        st.warning(f"No se encontraron credenciales para '{texto_url}'")

def main():
    st.title("🔍 Buscador de Credenciales")
    
    temp_dir = mkdtemp()
    
    st.write("### 📤 Subir Archivo Comprimido")
    archivo = st.file_uploader(
        "Arrastra aquí tu archivo RAR o ZIP", 
        type=['rar', 'zip']
    )
    
    texto_busqueda = st.text_input("🔎 Ingresa el texto a buscar en las URLs:")
    password_rar = st.text_input("🔑 Contraseña del archivo (si tiene):", type="password")
    
    if archivo:
        temp_file_path = os.path.join(temp_dir, archivo.name)
        with open(temp_file_path, 'wb') as f:
            f.write(archivo.getvalue())
        
        if st.button('Procesar Archivo'):
            with st.spinner("Procesando archivo..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    sleep(0.01)
                    progress_bar.progress(i + 1)
                
                passwords_dir = procesar_archivo_comprimido(temp_file_path, temp_dir, password_rar)
                if passwords_dir and texto_busqueda:
                    buscar_credenciales_por_url(passwords_dir, texto_busqueda)

if __name__ == "__main__":
    main()
