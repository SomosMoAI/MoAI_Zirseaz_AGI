"""
Zirseaz Failure Learner — Aprende de errores para no repetirlos.

Cuando exec() falla, almacena el patrón de error en memoria procedural.
Antes de ejecutar nuevo código, verifica si hay patrones conocidos.
"""
import os, sys, json, time, re

_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")
_SKILLS_REPO = os.path.join(_SKILL_ROOT, "skills_repo")
if _SKILLS_REPO not in sys.path:
    sys.path.insert(0, _SKILLS_REPO)

FAILURES_FILE = os.path.join(_SKILL_ROOT, "state", "failure_patterns.json")

def _load_patterns():
    if not os.path.exists(FAILURES_FILE):
        return {"patterns": []}
    try:
        with open(FAILURES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {"patterns": []}

def _save_patterns(data):
    os.makedirs(os.path.dirname(FAILURES_FILE), exist_ok=True)
    with open(FAILURES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def record_failure(code, error_output):
    """Registra un fallo de ejecución para aprendizaje."""
    data = _load_patterns()
    error_type = "unknown"
    match = re.search(r'(\w+Error):', error_output)
    if match:
        error_type = match.group(1)
    
    # Extraer módulos usados
    imports = re.findall(r'import\s+(\w+)', code)
    
    pattern = {
        "error_type": error_type,
        "error_snippet": error_output[:200],
        "code_snippet": code[:300],
        "imports_used": imports,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "count": 1
    }
    
    # Verificar si ya existe un patrón similar
    for existing in data["patterns"]:
        if existing["error_type"] == error_type and any(imp in existing.get("imports_used", []) for imp in imports):
            existing["count"] = existing.get("count", 1) + 1
            existing["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            _save_patterns(data)
            return
    
    data["patterns"].append(pattern)
    # Mantener máx 50 patrones
    if len(data["patterns"]) > 50:
        data["patterns"] = sorted(data["patterns"], key=lambda x: x.get("count", 0), reverse=True)[:50]
    _save_patterns(data)
    
    # También guardar en memoria procedural
    try:
        import memory_manager
        memory_manager.add_memory(
            f"Error aprendido [{error_type}]: {error_output[:100]}. Codigo que fallo usaba: {', '.join(imports[:5])}",
            category="procedural"
        )
    except: pass

def get_warnings_for_code(code):
    """Revisa si el código tiene patrones que han fallado antes."""
    data = _load_patterns()
    warnings = []
    imports = re.findall(r'import\s+(\w+)', code)
    
    for pattern in data["patterns"]:
        if pattern.get("count", 0) >= 2:
            common = set(imports) & set(pattern.get("imports_used", []))
            if common:
                warnings.append(f"ADVERTENCIA: Modulos {common} han causado {pattern['error_type']} antes ({pattern['count']}x)")
    
    # Detectar anti-patrones conocidos
    if "os.walk('/')" in code or 'os.walk("/")' in code or "os.walk('\\\\')" in code:
        warnings.append("BLOQUEADO: os.walk('/') esta prohibido (congela el bot)")
    if "while True" in code and "break" not in code and "time.sleep" not in code:
        warnings.append("ADVERTENCIA: Loop infinito detectado sin break ni sleep")
    if "shutil.rmtree" in code:
        warnings.append("PELIGRO: shutil.rmtree detectado. Requiere aprobacion HITL.")
    
    return warnings

def get_failure_stats():
    data = _load_patterns()
    if not data["patterns"]:
        return "No hay patrones de error registrados."
    lines = ["Patrones de error conocidos:"]
    for p in sorted(data["patterns"], key=lambda x: x.get("count", 0), reverse=True)[:10]:
        lines.append(f"  [{p['error_type']}] x{p.get('count',1)}: {p.get('error_snippet','')[:60]}...")
    return "\n".join(lines)
