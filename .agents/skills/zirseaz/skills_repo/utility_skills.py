import os
import shutil
import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
import hashlib
import re

# --- GESTIÓN DE ARCHIVOS ---

def leer_archivo(ruta):
    """Lee el contenido de un archivo de texto."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error al leer archivo: {e}"

def escribir_archivo(ruta, contenido):
    """Escribe contenido en un archivo de texto."""
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"Archivo '{ruta}' escrito exitosamente."
    except Exception as e:
        return f"Error al escribir archivo: {e}"

def listar_directorio(ruta="."):
    """Lista los archivos y carpetas en una ruta."""
    try:
        files = os.listdir(ruta)
        return f"Archivos en {ruta}:\n" + "\n".join(files)
    except Exception as e:
        return f"Error al listar directorio: {e}"

def eliminar_archivo(ruta):
    """Elimina un archivo del sistema."""
    try:
        os.remove(ruta)
        return f"Archivo '{ruta}' eliminado."
    except Exception as e:
        return f"Error al eliminar archivo: {e}"

def crear_carpeta(ruta):
    """Crea una carpeta si no existe."""
    try:
        os.makedirs(ruta, exist_ok=True)
        return f"Carpeta '{ruta}' creada o ya existente."
    except Exception as e:
        return f"Error al crear carpeta: {e}"

# --- SISTEMA Y ENTORNO ---

def obtener_info_sistema():
    """Devuelve informacion basica del sistema operativo."""
    import platform
    return f"SO: {platform.system()} {platform.release()} | Python: {platform.python_version()}"

def obtener_hora_actual():
    """Devuelve la fecha y hora actual."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def tamano_archivo(ruta):
    """Devuelve el tamaño de un archivo en bytes."""
    try:
        return f"{os.path.getsize(ruta)} bytes"
    except Exception as e:
        return f"Error: {e}"

def buscar_archivos_por_extension(directorio, extension):
    """Busca archivos con una extension especifica en un directorio."""
    try:
        files = os.listdir(directorio)
        filtered = [f for f in files if f.endswith(extension)]
        return f"Archivos {extension} en {directorio}:\n" + "\n".join(filtered)
    except Exception as e:
        return f"Error: {e}"

def obtener_ruta_actual():
    """Devuelve el directorio de trabajo actual."""
    return os.getcwd()

# --- PROCESAMIENTO DE TEXTO Y DATOS ---

def contar_palabras(texto):
    """Cuenta las palabras en un texto."""
    words = texto.split()
    return f"El texto tiene {len(words)} palabras."

def extraer_urls(texto):
    """Extrae URLs de un texto usando regex."""
    urls = re.findall(r'(https?://[^\s]+)', texto)
    return "URLs encontradas:\n" + "\n".join(urls) if urls else "No se encontraron URLs."

def reemplazar_texto_en_archivo(ruta, viejo, nuevo):
    """Reemplaza una cadena por otra en un archivo."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = content.replace(viejo, nuevo)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(new_content)
        return f"Texto reemplazado en '{ruta}'."
    except Exception as e:
        return f"Error: {e}"

def calcular_hash_archivo(ruta):
    """Calcula el hash MD5 de un archivo."""
    try:
        hasher = hashlib.md5()
        with open(ruta, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return f"MD5 de {ruta}: {hasher.hexdigest()}"
    except Exception as e:
        return f"Error: {e}"

def formatear_json(texto_json):
    """Intenta formatear un texto JSON para que sea legible."""
    try:
        data = json.loads(texto_json)
        return json.dumps(data, indent=4, ensure_ascii=False)
    except Exception as e:
        return f"JSON no valido: {e}"

# --- RED Y CONEXIONES ---

def descargar_archivo(url, ruta_destino):
    """Descarga un archivo desde una URL."""
    try:
        urllib.request.urlretrieve(url, ruta_destino)
        return f"Archivo descargado en: {ruta_destino}"
    except Exception as e:
        return f"Error al descargar: {e}"

def obtener_ip_publica():
    """Devuelve la IP publica del servidor."""
    try:
        req = urllib.request.Request("https://api.ipify.org?format=json")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            return f"IP Publica: {data['ip']}"
    except Exception as e:
        return f"Error al obtener IP: {e}"

def verificar_sitio_web(url):
    """Verifica si un sitio web responde (Status Code)."""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            return f"El sitio {url} respondio con codigo: {response.status}"
    except Exception as e:
        return f"Error al conectar con {url}: {e}"

def enviar_peticion_get(url):
    """Envia una peticion GET y devuelve el contenido."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.read().decode('utf-8')[:1000] # Truncamos a 1000
    except Exception as e:
        return f"Error en peticion GET: {e}"

def enviar_peticion_post(url, data_json):
    """Envia una peticion POST con datos JSON."""
    try:
        data = data_json.encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.read().decode('utf-8')[:1000]
    except Exception as e:
        return f"Error en peticion POST: {e}"
