"""
Zirseaz Hosting Manager v2 — Deploy FTP al hosting.
Usa env_loader centralizado.
"""
import os
import sys
import ftplib
import io

# Asegurar imports desde utils/
_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

try:
    import env_loader
except ImportError:
    env_loader = None


def _get_hosting_credentials():
    """Obtiene credenciales de hosting con fallback."""
    if env_loader:
        return env_loader.get_hosting_credentials()
    
    host = os.environ.get("HOSTING_HOST")
    user = os.environ.get("HOSTING_USER")
    password = os.environ.get("HOSTING_PASS")
    
    if not (host and user and password):
        env_path = os.path.join(os.getcwd(), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("HOSTING_HOST="):
                        host = line.split("=")[1].strip()
                    elif line.startswith("HOSTING_USER="):
                        user = line.split("=")[1].strip()
                    elif line.startswith("HOSTING_PASS="):
                        password = line.split("=")[1].strip()
                        
    return host, user, password


def deploy_to_hosting(remote_dir, files_dict):
    """
    Sube archivos al hosting vía FTP.
    - remote_dir: Carpeta remota (ej. "/public_html/mi_proyecto")
    - files_dict: Diccionario de { "nombre_archivo.html": "contenido del archivo..." }
    """
    host, user, password = _get_hosting_credentials()
    if not (host and user and password):
        return "Error: Faltan credenciales HOSTING_HOST, HOSTING_USER o HOSTING_PASS."
        
    try:
        ftp = ftplib.FTP(host, timeout=15)
        ftp.login(user, password)
        
        # Navegar o crear el directorio remoto
        dirs = remote_dir.strip("/").split("/")
        current = ""
        for d in dirs:
            if not d:
                continue
            current += f"/{d}"
            try:
                ftp.cwd(current)
            except ftplib.error_perm:
                try:
                    ftp.mkd(current)
                    ftp.cwd(current)
                except Exception as e:
                    ftp.quit()
                    return f"Error al crear directorio {current}: {e}"
        
        # Subir los archivos
        uploaded = []
        for filename, content in files_dict.items():
            bio = io.BytesIO(content.encode('utf-8'))
            ftp.storbinary(f"STOR {filename}", bio)
            uploaded.append(filename)
            
        ftp.quit()
        return f"Exito: Despliegue completado en {host}{remote_dir}. Archivos: {', '.join(uploaded)}"
        
    except Exception as e:
        return f"Error critico FTP: {e}"


def list_remote_files(remote_dir="/"):
    """Lista archivos en un directorio remoto del hosting."""
    host, user, password = _get_hosting_credentials()
    if not (host and user and password):
        return "Error: Faltan credenciales de hosting."
    
    try:
        ftp = ftplib.FTP(host, timeout=15)
        ftp.login(user, password)
        ftp.cwd(remote_dir)
        files = ftp.nlst()
        ftp.quit()
        return f"Archivos en {remote_dir}:\n" + "\n".join(files)
    except Exception as e:
        return f"Error listando archivos: {e}"
