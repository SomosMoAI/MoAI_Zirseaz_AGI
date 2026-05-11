"""
Zirseaz Dashboard Generator — Genera un panel HTML estático desplegable al hosting.
Lee el estado actual del agente y genera un dashboard visual.
"""
import os, sys, json, time

_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")
_SKILLS_REPO = os.path.join(_SKILL_ROOT, "skills_repo")
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
for d in [_SKILLS_REPO, _UTILS_DIR]:
    if d not in sys.path: sys.path.insert(0, d)

def _get_memory_data():
    try:
        import memory_manager
        return memory_manager.get_memory_stats()
    except: return "N/A"

def _get_plugins_data():
    path = os.path.join(_SKILL_ROOT, "plugins.json")
    if not os.path.exists(path): return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return list(json.load(f).get("plugins", {}).keys())
    except: return []

def _get_objectives():
    try:
        import memory_manager
        return memory_manager.get_pending_objectives()
    except: return "N/A"

def generate_dashboard_html():
    """Genera el HTML completo del dashboard de Zirseaz."""
    mem_stats = _get_memory_data()
    plugins = _get_plugins_data()
    objectives = _get_objectives()
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    
    plugin_cards = ""
    colors = ["#6366f1","#8b5cf6","#ec4899","#f43f5e","#f97316","#eab308","#22c55e","#06b6d4","#3b82f6","#a855f7"]
    for i, p in enumerate(plugins):
        c = colors[i % len(colors)]
        plugin_cards += f'<div class="card" style="border-left:4px solid {c}"><h3>{p}</h3></div>\n'
    
    obj_lines = objectives.replace("\n", "<br>") if objectives != "N/A" else "Sin objetivos"
    mem_lines = mem_stats.replace("\n", "<br>") if mem_stats != "N/A" else "Sin datos"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zirseaz v5 Cortex - Dashboard</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0a0a0f;color:#e2e8f0;min-height:100vh}}
.header{{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:2rem;text-align:center;border-bottom:2px solid #6366f1}}
.header h1{{font-size:2.5rem;background:linear-gradient(90deg,#6366f1,#8b5cf6,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem}}
.header p{{color:#94a3b8;font-size:0.9rem}}
.pulse{{display:inline-block;width:10px;height:10px;background:#22c55e;border-radius:50%;margin-right:8px;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:1.5rem;padding:2rem;max-width:1200px;margin:0 auto}}
.section{{background:#1a1a2e;border-radius:12px;padding:1.5rem;border:1px solid #2a2a4e}}
.section h2{{color:#8b5cf6;margin-bottom:1rem;font-size:1.3rem;display:flex;align-items:center;gap:8px}}
.section h2::before{{content:'';display:inline-block;width:4px;height:20px;background:linear-gradient(180deg,#6366f1,#ec4899);border-radius:2px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:0.5rem}}
.card{{background:#12121e;border-radius:8px;padding:0.8rem;font-size:0.85rem;transition:transform 0.2s}}
.card:hover{{transform:translateY(-2px)}}
.card h3{{font-size:0.8rem;color:#c4b5fd}}
.stat{{font-size:0.9rem;line-height:1.6;color:#94a3b8}}
.footer{{text-align:center;padding:1.5rem;color:#475569;font-size:0.8rem;border-top:1px solid #1e1e3e}}
.badge{{display:inline-block;background:#6366f133;color:#a5b4fc;padding:2px 8px;border-radius:4px;font-size:0.75rem;margin:2px}}
</style>
</head>
<body>
<div class="header">
<h1>ZIRSEAZ v5 CORTEX</h1>
<p><span class="pulse"></span>Meta-Agente Autonomo AGI &mdash; Ultima actualizacion: {now}</p>
</div>
<div class="grid">
<div class="section">
<h2>Memoria</h2>
<div class="stat">{mem_lines}</div>
</div>
<div class="section">
<h2>Micro-Objetivos</h2>
<div class="stat">{obj_lines}</div>
</div>
<div class="section" style="grid-column:1/-1">
<h2>Plugins Registrados ({len(plugins)})</h2>
<div class="cards">{plugin_cards}</div>
</div>
<div class="section">
<h2>Arquitectura</h2>
<div class="stat">
<span class="badge">Cortex ReAct</span>
<span class="badge">Semantic Memory</span>
<span class="badge">Plugin Registry</span>
<span class="badge">Smart Router</span>
<span class="badge">Quarantine</span>
<span class="badge">Failure Learning</span>
<span class="badge">Context Manager</span>
<span class="badge">Session Persistence</span>
</div>
</div>
</div>
<div class="footer">Zirseaz v5 Cortex &mdash; Forjado por el Lider &mdash; Evolucion autonoma desde 2026</div>
</body>
</html>"""
    return html

def deploy_dashboard():
    """Genera y despliega el dashboard al hosting."""
    html = generate_dashboard_html()
    try:
        import hosting_manager
        result = hosting_manager.deploy_to_hosting("/public_html/zirseaz", {"index.html": html})
        return result
    except Exception as e:
        # Fallback: guardar localmente
        local_path = os.path.join(_SKILL_ROOT, "state", "dashboard.html")
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(html)
        return f"Dashboard guardado localmente en {local_path} (deploy fallo: {e})"
