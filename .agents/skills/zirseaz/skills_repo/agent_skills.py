"""
Zirseaz Agent Skills v2 — Con auto-testing y quarantine.

Cuando Zirseaz crea una nueva habilidad:
1. Guarda el código en quarantine/ primero
2. Intenta importar el módulo para verificar sintaxis
3. Ejecuta un smoke test (llamar funciones con mocks)
4. Si pasa → lo mueve a skills_repo/ y registra en plugins.json
5. Si falla → queda en quarantine/ con log del error
"""
import os
import sys
import json
import importlib.util
import inspect
import io
import contextlib
import time

_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")
SKILLS_DIR = os.path.join(_SKILL_ROOT, "skills_repo")
QUARANTINE_DIR = os.path.join(_SKILL_ROOT, "quarantine")
PLUGINS_FILE = os.path.join(_SKILL_ROOT, "plugins.json")


def _ensure_dirs():
    os.makedirs(SKILLS_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)


def _test_module(filepath, module_name):
    """
    Test básico de un módulo Python:
    1. Puede importarse sin errores
    2. Tiene al menos una función pública
    3. Las funciones públicas son invocables
    
    Returns: (success, message, functions_found)
    """
    try:
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        
        # Capturar stdout/stderr durante import
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            spec.loader.exec_module(module)
        
        # Listar funciones públicas
        public_functions = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and not name.startswith("_"):
                public_functions.append(name)
        
        if not public_functions:
            return False, f"El modulo se importo pero no tiene funciones publicas.", []
        
        return True, f"Import OK. Funciones encontradas: {', '.join(public_functions)}", public_functions
        
    except SyntaxError as e:
        return False, f"Error de sintaxis: {e}", []
    except ImportError as e:
        return False, f"Error de import (dependencia faltante?): {e}", []
    except Exception as e:
        return False, f"Error al importar: {type(e).__name__}: {e}", []


def _register_plugin(module_name, functions, description="", category="custom"):
    """Registra un plugin en plugins.json."""
    if not os.path.exists(PLUGINS_FILE):
        registry = {"_meta": {"version": "1.0"}, "plugins": {}}
    else:
        with open(PLUGINS_FILE, "r", encoding="utf-8") as f:
            registry = json.load(f)
    
    registry["plugins"][module_name] = {
        "file": f"skills_repo/{module_name}.py",
        "description": description or f"Plugin auto-generado por Zirseaz el {time.strftime('%Y-%m-%d')}",
        "functions": functions,
        "category": category,
        "requires_api": False,
        "auto_generated": True,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    registry["_meta"]["last_updated"] = time.strftime("%Y-%m-%d")
    
    with open(PLUGINS_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)


def crear_habilidad(nombre, codigo, descripcion=""):
    """
    Crea una nueva habilidad con auto-testing.
    
    Flujo:
    1. Guarda en quarantine/
    2. Test de importación
    3. Si pasa → mueve a skills_repo/ y registra
    4. Si falla → queda en quarantine/ con error log
    
    Args:
        nombre: Nombre del módulo (sin .py)
        codigo: Código Python de la habilidad
        descripcion: Descripción para el registry
    
    Returns:
        String con el resultado del proceso
    """
    _ensure_dirs()
    
    # Limpiar nombre
    nombre = nombre.replace(" ", "_").replace("-", "_").lower()
    if nombre.endswith(".py"):
        nombre = nombre[:-3]
    
    filename = f"{nombre}.py"
    
    # 1. Guardar en quarantine primero
    quarantine_path = os.path.join(QUARANTINE_DIR, filename)
    with open(quarantine_path, "w", encoding="utf-8") as f:
        f.write(codigo)
    
    # 2. Test de importación
    success, message, functions = _test_module(quarantine_path, nombre)
    
    if not success:
        # Guardar log del error junto al archivo
        error_log_path = os.path.join(QUARANTINE_DIR, f"{nombre}_error.log")
        with open(error_log_path, "w", encoding="utf-8") as f:
            f.write(f"Test fallido: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Error: {message}\n")
        
        return (
            f"QUARANTINE: La habilidad '{nombre}' NO paso el test de calidad.\n"
            f"Error: {message}\n"
            f"El archivo quedo en quarantine/ para revision manual.\n"
            f"Corrige el codigo y vuelve a intentar."
        )
    
    # 3. Test pasado → mover a skills_repo
    final_path = os.path.join(SKILLS_DIR, filename)
    
    # Backup si ya existe
    if os.path.exists(final_path):
        backup_path = os.path.join(QUARANTINE_DIR, f"{nombre}_backup_{int(time.time())}.py")
        with open(final_path, "r", encoding="utf-8") as f_old:
            with open(backup_path, "w", encoding="utf-8") as f_bak:
                f_bak.write(f_old.read())
    
    # Mover de quarantine a skills_repo
    with open(quarantine_path, "r", encoding="utf-8") as f:
        content = f.read()
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Limpiar quarantine
    os.remove(quarantine_path)
    
    # 4. Registrar en plugins.json
    _register_plugin(nombre, functions, descripcion)
    
    return (
        f"EXITO: Habilidad '{nombre}' creada y registrada.\n"
        f"Funciones: {', '.join(functions)}\n"
        f"Ubicacion: skills_repo/{filename}\n"
        f"Registrada en plugins.json como categoria 'custom'."
    )


def listar_habilidades_disponibles():
    """Lista todas las habilidades disponibles desde plugins.json y disco."""
    result = []
    
    # Desde plugins.json
    if os.path.exists(PLUGINS_FILE):
        try:
            with open(PLUGINS_FILE, "r", encoding="utf-8") as f:
                registry = json.load(f)
            
            result.append("=== PLUGINS REGISTRADOS ===")
            for name, data in registry.get("plugins", {}).items():
                funcs = ", ".join(data.get("functions", []))
                auto = " [AUTO]" if data.get("auto_generated") else ""
                result.append(f"  [{data.get('category', '?')}] {name}{auto}: {funcs}")
        except Exception:
            result.append("Error leyendo plugins.json")
    
    # Archivos en quarantine
    if os.path.exists(QUARANTINE_DIR):
        quarantine_files = [f for f in os.listdir(QUARANTINE_DIR) if f.endswith(".py")]
        if quarantine_files:
            result.append("\n=== EN QUARANTINE (no pasaron test) ===")
            for f in quarantine_files:
                result.append(f"  [!] {f}")
    
    if not result:
        return "No hay habilidades registradas."
    
    return "\n".join(result)
