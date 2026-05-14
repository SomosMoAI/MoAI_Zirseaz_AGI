"""
Zirseaz Dashboard Generator — Genera un panel HTML interactivo y responsivo.
Lee el estado actual del agente, la sesion y genera un dashboard visual.
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
            plugins = json.load(f).get("plugins", {})
            return [{"name": k, "desc": v.get("description", ""), "cat": v.get("category", "unknown")} for k,v in plugins.items()]
    except: return []

def _get_objectives():
    try:
        import memory_manager
        return memory_manager.get_pending_objectives()
    except: return "N/A"

def _get_router_data():
    try:
        import llm_router
        return llm_router.get_router_stats()
    except: return "N/A"

def _get_token_data():
    try:
        import token_tracker
        return token_tracker.get_usage_report()
    except: return "N/A"

def _get_conversation():
    try:
        import session_manager
        history, meta = session_manager.load_latest_session()
        if not history: return []
        # Excluir el system prompt que es enorme
        chat = [m for m in history if m.get("role") != "system"]
        return chat[-10:] # Ultimos 10 mensajes
    except:
        return []

def generate_dashboard_html():
    """Genera el HTML completo del dashboard de Zirseaz v7."""
    mem_stats = _get_memory_data()
    plugins = _get_plugins_data()
    objectives = _get_objectives()
    router_stats = _get_router_data()
    token_stats = _get_token_data()
    chat = _get_conversation()
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Formatear Skills
    plugin_badges = ""
    for p in plugins:
        cat_colors = {"core": "#3b82f6", "research": "#8b5cf6", "system": "#f59e0b", "deployment": "#10b981", "communication": "#ec4899"}
        c = cat_colors.get(p.get("cat"), "#6b7280")
        plugin_badges += f'<span class="skill-badge" style="border-color:{c}; color:{c}" title="{p["desc"]}">{p["name"]}</span>'
    
    # Formatear Conversacion
    chat_html = ""
    if not chat:
        chat_html = "<div class='msg system'>No hay sesion activa guardada.</div>"
    for msg in chat:
        role = msg.get("role", "unknown")
        content = msg.get("content", "").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if role == "user":
            chat_html += f"<div class='msg user'><b>Humano:</b><br>{content}</div>"
        elif role == "assistant":
            # Extraer bloques de "Pensamiento" si existe etiqueta <think> o similares (simulado)
            if "Pensando..." in content or "Plan:" in content:
                chat_html += f"<div class='msg think'><b>Zirseaz (Procesando):</b><br>{content}</div>"
            else:
                chat_html += f"<div class='msg assistant'><b>Zirseaz:</b><br>{content}</div>"
    
    obj_lines = objectives.replace("\n", "<br>") if objectives != "N/A" else "Sin objetivos"
    mem_lines = mem_stats.replace("\n", "<br>") if mem_stats != "N/A" else "Sin datos"
    router_lines = router_stats.replace("\n", "<br>") if router_stats != "N/A" else "Sin datos"
    token_lines = token_stats.replace("\n", "<br>") if token_stats != "N/A" else "Sin datos"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="15">
<title>Zirseaz v7 Ultimate Cortex - Live Dashboard</title>
<style>
:root {{
    --bg-dark: #0f111a;
    --bg-card: #1a1d2d;
    --text-main: #e2e8f0;
    --text-muted: #94a3b8;
    --accent-primary: #6366f1;
    --accent-secondary: #ec4899;
    --success: #10b981;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',system-ui,sans-serif;background:var(--bg-dark);color:var(--text-main);min-height:100vh;display:flex;flex-direction:column}}
.header{{background:linear-gradient(90deg, #111827 0%, #1e1b4b 100%);padding:1.5rem 2rem;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #3730a3;position:sticky;top:0;z-index:100}}
.header-left h1{{font-size:1.8rem;background:linear-gradient(90deg,var(--accent-primary),var(--accent-secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.header-left p{{color:var(--text-muted);font-size:0.85rem;margin-top:4px}}
.header-right{{display:flex;align-items:center;gap:12px;font-size:0.85rem;color:var(--success)}}
.pulse{{display:inline-block;width:10px;height:10px;background:var(--success);border-radius:50%;animation:pulse 2s infinite;box-shadow: 0 0 10px var(--success)}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}

.main-container {{display:flex;flex:1;overflow:hidden;flex-wrap:wrap;}}
.col-left {{flex: 1 1 400px; padding: 1.5rem; display:flex; flex-direction:column; border-right:1px solid #2a2e45; max-height: calc(100vh - 80px); overflow-y:auto;}}
.col-right {{flex: 2 1 600px; padding: 1.5rem; display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; align-content:start; max-height: calc(100vh - 80px); overflow-y:auto;}}

/* Seccion Chat */
.chat-box {{background:var(--bg-card);border-radius:12px;border:1px solid #2a2e45;padding:1rem;display:flex;flex-direction:column;gap:1rem;flex:1}}
.chat-title {{color:var(--text-muted);font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;display:flex;justify-content:space-between}}
.msg {{padding:1rem;border-radius:8px;font-size:0.95rem;line-height:1.5;animation:fadeIn 0.3s ease}}
@keyframes fadeIn {{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
.msg.user {{background:#1e293b;border-left:3px solid #38bdf8;margin-left:20%;color:#e0f2fe}}
.msg.assistant {{background:#312e81;border-left:3px solid var(--accent-primary);margin-right:20%;color:#e0e7ff}}
.msg.think {{background:#4c1d95;border-left:3px solid var(--accent-secondary);margin-right:20%;color:#fbcfe8;font-style:italic;font-size:0.9rem}}
.msg.system {{background:#0f172a;color:var(--text-muted);text-align:center;font-size:0.85rem}}

/* Secciones Estado */
.section {{background:var(--bg-card);border-radius:12px;padding:1.5rem;border:1px solid #2a2e45;transition:all 0.3s}}
.section:hover {{border-color:var(--accent-primary);box-shadow: 0 4px 20px rgba(99, 102, 241, 0.1)}}
.section h2 {{color:#c4b5fd;font-size:1.1rem;margin-bottom:1rem;display:flex;align-items:center;gap:8px;border-bottom:1px solid #2a2e45;padding-bottom:0.5rem}}
.stat {{font-size:0.9rem;line-height:1.6;color:var(--text-muted);font-family:monospace;white-space:pre-wrap;}}

/* Skills Badges */
.skills-container {{display:flex;flex-wrap:wrap;gap:8px}}
.skill-badge {{padding:4px 10px;border-radius:20px;font-size:0.75rem;font-weight:600;border:1px solid;background:rgba(255,255,255,0.05);cursor:help;transition:transform 0.2s}}
.skill-badge:hover {{transform:scale(1.05);background:rgba(255,255,255,0.1)}}

/* Scrollbar */
::-webkit-scrollbar {{width:8px}}
::-webkit-scrollbar-track {{background:var(--bg-dark)}}
::-webkit-scrollbar-thumb {{background:#374151;border-radius:4px}}
::-webkit-scrollbar-thumb:hover {{background:var(--accent-primary)}}

@media (max-width: 900px) {{
    .main-container {{flex-direction:column}}
    .col-left, .col-right {{max-height:none;border-right:none;overflow:visible}}
}}
</style>
</head>
<body>
<div class="header">
    <div class="header-left">
        <h1>Zirseaz Cortex Dashboard</h1>
        <p>AGI Framework v7.5 &mdash; Módulo de Consciencia</p>
    </div>
    <div class="header-right">
        <span class="pulse"></span> Online ({now})
    </div>
</div>

<div class="main-container">
    <!-- Columna Izquierda: Conversación en Vivo -->
    <div class="col-left">
        <div class="chat-title">
            <span>🔴 Feed de Interacción</span>
            <span>Auto-Refresh: 15s</span>
        </div>
        <div class="chat-box">
            {chat_html}
        </div>
    </div>

    <!-- Columna Derecha: Estado del Agente -->
    <div class="col-right">
        <div class="section" style="grid-column: 1 / -1">
            <h2>🧠 Skills Adquiridas ({len(plugins)})</h2>
            <div class="skills-container">{plugin_badges}</div>
        </div>
        <div class="section">
            <h2>📊 LLM Router & Costos</h2>
            <div class="stat">{router_lines}<br><hr style="border-color:#2a2e45;margin:8px 0"><br>{token_lines}</div>
        </div>
        <div class="section">
            <h2>🎯 Objetivos & Planeación</h2>
            <div class="stat">{obj_lines}</div>
        </div>
        <div class="section" style="grid-column: 1 / -1">
            <h2>💾 Memoria Core</h2>
            <div class="stat">{mem_lines}</div>
        </div>
    </div>
</div>
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
