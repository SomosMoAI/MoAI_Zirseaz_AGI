import os
import sys
import json
import time

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PLUGINS_JSON = os.path.join(_SKILL_ROOT, "plugins.json")
_SKILLS_REPO_DIR = os.path.join(_SKILL_ROOT, "skills_repo")

def run_in_sandbox(code_str, test_function_name, *test_args):
    """
    Ejecuta un codigo en un entorno aislado y prueba una funcion especifica.
    Retorna (success, output_or_error)
    """
    safe_builtins = {k: v for k, v in __builtins__.__dict__.items() if k not in (
        'exec', 'eval', 'compile', '__import__', 'exit', 'quit'
    )} if hasattr(__builtins__, '__dict__') else {}
    
    ctx = {
        "__builtins__": safe_builtins,
    }
    
    # Imports seguros
    import json as _json, time as _time, math as _math, re as _re
    ctx.update({"json": _json, "time": _time, "math": _math, "re": _re})
    try:
        import requests as _requests
        ctx["requests"] = _requests
    except:
        pass
    
    try:
        exec(code_str, ctx)
        if test_function_name not in ctx:
            return False, f"La funcion de prueba '{test_function_name}' no se encontro en el codigo generado."
        
        func = ctx[test_function_name]
        start_time = time.time()
        result = func(*test_args)
        elapsed = time.time() - start_time
        if elapsed > 10:
            return False, "Ejecucion excedio los 10 segundos. Bucle infinito detectado (Circuit Breaker)."
            
        return True, result
    except Exception as e:
        import traceback
        return False, traceback.format_exc()

def forge_plugin(plugin_name, description, category, code_str, test_function_name, *test_args):
    """
    Recibe el codigo de un nuevo plugin, lo prueba en el sandbox, 
    y si pasa, lo instala en skills_repo y actualiza plugins.json.
    
    Args:
        plugin_name: Nombre corto sin .py
        description: Breve explicacion de lo que hace
        category: core, research, system, custom
        code_str: El codigo python crudo a compilar
        test_function_name: La funcion principal a llamar para probar
        test_args: Argumentos mockeados para pasarle a la funcion de prueba
    """
    success, result = run_in_sandbox(code_str, test_function_name, *test_args)
    if not success:
        return False, f"El codigo fallo en el Sandbox de Pruebas:\n{result}"
        
    # Guardar archivo
    plugin_path = os.path.join(_SKILLS_REPO_DIR, f"{plugin_name}.py")
    try:
        with open(plugin_path, "w", encoding="utf-8") as f:
            f.write(code_str)
    except Exception as e:
        return False, f"Error guardando el archivo del plugin: {e}"
        
    # Actualizar plugins.json
    try:
        with open(_PLUGINS_JSON, "r", encoding="utf-8") as f:
            registry = json.load(f)
            
        # Extraer nombres de funciones
        import ast
        tree = ast.parse(code_str)
        funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")]
        
        if "plugins" not in registry:
            registry["plugins"] = {}
            
        registry["plugins"][plugin_name] = {
            "file": f"skills_repo/{plugin_name}.py",
            "description": description,
            "functions": funcs,
            "category": category,
            "requires_api": False,
            "auto_forged": True,
            "forged_at": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        with open(_PLUGINS_JSON, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=4)
            
    except Exception as e:
        return False, f"Plugin guardado pero fallo al registrar en plugins.json: {e}"
        
    return True, f"Plugin '{plugin_name}' forjado e instalado exitosamente. Resultado del test simulado: {result}"
