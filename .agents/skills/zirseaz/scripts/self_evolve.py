"""
Zirseaz Self-Evolution Engine — Se lee, se analiza, se mejora.

Capacidades:
1. Leer su propio código fuente
2. Analizar con LLM qué se puede mejorar
3. Generar parches
4. Aplicar parches (con HITL)
5. Registrar evoluciones en memoria
"""
import os, sys, json, time, difflib

_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")


def read_own_source(module_name):
    """Lee el código fuente de un módulo propio."""
    locations = [
        os.path.join(_SKILL_ROOT, "scripts", f"{module_name}.py"),
        os.path.join(_SKILL_ROOT, "skills_repo", f"{module_name}.py"),
        os.path.join(_SKILL_ROOT, "utils", f"{module_name}.py"),
    ]
    for path in locations:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read(), path
    return None, None


def list_own_modules():
    """Lista todos los módulos que componen a Zirseaz."""
    modules = []
    for subdir in ["scripts", "skills_repo", "utils"]:
        dirpath = os.path.join(_SKILL_ROOT, subdir)
        if os.path.exists(dirpath):
            for f in os.listdir(dirpath):
                if f.endswith(".py") and not f.startswith("test_"):
                    filepath = os.path.join(dirpath, f)
                    size = os.path.getsize(filepath)
                    lines = 0
                    try:
                        with open(filepath, "r", encoding="utf-8") as fh:
                            lines = sum(1 for _ in fh)
                    except: pass
                    modules.append({
                        "name": f[:-3],
                        "dir": subdir,
                        "path": filepath,
                        "size_bytes": size,
                        "lines": lines
                    })
    return modules


def get_self_inventory():
    """Retorna un inventario legible de todos los módulos propios."""
    modules = list_own_modules()
    total_lines = sum(m["lines"] for m in modules)
    total_bytes = sum(m["size_bytes"] for m in modules)
    
    lines = [f"Inventario de Zirseaz: {len(modules)} modulos, {total_lines} lineas, {total_bytes//1024}KB"]
    for subdir in ["scripts", "skills_repo", "utils"]:
        group = [m for m in modules if m["dir"] == subdir]
        if group:
            lines.append(f"\n  === {subdir}/ ===")
            for m in sorted(group, key=lambda x: -x["lines"]):
                lines.append(f"    {m['name']}.py: {m['lines']} lineas ({m['size_bytes']//1024}KB)")
    return "\n".join(lines)


def generate_patch(original_code, new_code, filename="module.py"):
    """Genera un diff legible entre dos versiones de código."""
    original_lines = original_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)
    diff = difflib.unified_diff(original_lines, new_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}", lineterm="")
    return "\n".join(diff)


def apply_patch(module_name, new_code):
    """
    Aplica un parche a un módulo propio.
    REQUIERE HITL — solo usar después de aprobación.
    
    Flujo:
    1. Lee el código actual
    2. Crea backup
    3. Escribe el nuevo código
    4. Intenta importar para verificar
    5. Si falla, restaura backup
    6. Registra en memoria
    """
    current_code, filepath = read_own_source(module_name)
    if not filepath:
        return f"Error: Modulo '{module_name}' no encontrado."
    
    # Backup
    backup_dir = os.path.join(_SKILL_ROOT, "state", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"{module_name}_{int(time.time())}.py.bak")
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(current_code)
    
    # Escribir nuevo código
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_code)
    
    # Verificar que importa
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        # Restaurar backup
        with open(backup_path, "r", encoding="utf-8") as f:
            restored = f.read()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(restored)
        return f"ROLLBACK: El parche rompio el modulo. Error: {e}. Se restauro la version anterior."
    
    # Registrar en memoria
    try:
        skills_repo = os.path.join(_SKILL_ROOT, "skills_repo")
        if skills_repo not in sys.path:
            sys.path.insert(0, skills_repo)
        import memory_manager
        diff = generate_patch(current_code, new_code, f"{module_name}.py")
        diff_summary = diff[:300] if diff else "Sin cambios visibles"
        memory_manager.add_memory(
            f"Auto-evolucion: Modifique {module_name}.py. Cambios: {diff_summary}",
            category="episodic"
        )
    except: pass
    
    return f"EXITO: Modulo '{module_name}' actualizado. Backup en {backup_path}."


def get_evolution_history():
    """Retorna el historial de evoluciones desde la memoria."""
    try:
        skills_repo = os.path.join(_SKILL_ROOT, "skills_repo")
        if skills_repo not in sys.path:
            sys.path.insert(0, skills_repo)
        import memory_manager
        results = memory_manager.search_memory("auto-evolucion modifique", max_results=10)
        return results
    except:
        return "No se pudo leer historial de evoluciones."
