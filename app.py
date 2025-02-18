import streamlit as st
import os
import rarfile
import shutil

def descomprimir_rar(archivo_rar, carpeta_destino, password):
    try:
        os.makedirs(carpeta_destino, exist_ok=True)
        with rarfile.RarFile(archivo_rar) as rf:
            rf.extractall(carpeta_destino, pwd=password.encode())
        return True, "Archivo RAR descomprimido con éxito."
    except rarfile.BadRarFile:
        return False, "Error: Archivo RAR inválido o contraseña incorrecta."
    except Exception as e:
        return False, f"Error inesperado: {e}"

def buscar_archivos(carpeta_destino, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    encontrados = []
    for root, _, files in os.walk(carpeta_destino):
        for filename in files:
            if filename.lower() in ('password.txt', 'passwords.txt'):
                shutil.copy(os.path.join(root, filename), os.path.join(output_folder, filename))
                encontrados.append(filename)
    return encontrados

st.title("Extracción de Contraseñas desde Archivos RAR")

archivo_subido = st.file_uploader("Sube un archivo .rar", type=["rar"])
password = st.text_input("Introduce la contraseña para descomprimir", type="password")

if archivo_subido and password:
    carpeta_destino = "descomprimido"
    output_folder = "PASSWORD"
    
    with open("temp.rar", "wb") as f:
        f.write(archivo_subido.getbuffer())
    
    exito, mensaje = descomprimir_rar("temp.rar", carpeta_destino, password)
    st.write(mensaje)
    
    if exito:
        archivos_encontrados = buscar_archivos(carpeta_destino, output_folder)
        if archivos_encontrados:
            st.write("Archivos de contraseñas encontrados y copiados:")
            st.write(archivos_encontrados)
        else:
            st.write("No se encontraron archivos de contraseñas.")
    
    os.remove("temp.rar")
