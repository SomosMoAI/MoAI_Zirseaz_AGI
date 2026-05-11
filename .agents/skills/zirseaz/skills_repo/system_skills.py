import subprocess
import sys

def ejecutar_comando(cmd):
    """Ejecuta un comando en la terminal del sistema (Windows/Linux) y devuelve la salida."""
    try:
        # Usamos shell=True para permitir comandos compuestos
        # En Windows usamos chcp 65001 para forzar UTF-8 en la salida del comando si es necesario
        if sys.platform == "win32" and not cmd.startswith("chcp"):
            cmd = "chcp 65001 > nul && " + cmd
            
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
            
        if not output:
            output = "Comando ejecutado sin salida."
            
        return output
    except Exception as e:
        return f"Error al ejecutar comando: {e}"
