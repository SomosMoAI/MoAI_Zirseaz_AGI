"""
Zirseaz Scheduler — Programador de tareas autónomas.

Permite que Zirseaz programe tareas recurrentes o puntuales:
- "Cada 30 min revisa mis objetivos"
- "Cada 6 horas genera un reporte de dashboard"
- "Mañana a las 9 envía un email"

Las tareas se persisten en disco y sobreviven reinicios.
"""
import os, json, time, threading

STATE_DIR = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "state")
SCHEDULE_FILE = os.path.join(STATE_DIR, "scheduled_tasks.json")


def _load_tasks():
    if not os.path.exists(SCHEDULE_FILE):
        return {"tasks": []}
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"tasks": []}


def _save_tasks(data):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_recurring_task(name, code, interval_seconds, description=""):
    """
    Programa una tarea recurrente.
    
    Args:
        name: Identificador único de la tarea
        code: Código Python a ejecutar
        interval_seconds: Intervalo en segundos entre ejecuciones
        description: Descripción humana
    """
    data = _load_tasks()
    # Evitar duplicados
    data["tasks"] = [t for t in data["tasks"] if t.get("name") != name]
    data["tasks"].append({
        "name": name,
        "type": "recurring",
        "code": code,
        "interval": interval_seconds,
        "description": description,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "last_run": None,
        "run_count": 0,
        "enabled": True
    })
    _save_tasks(data)
    return f"Tarea recurrente '{name}' programada cada {interval_seconds}s."


def add_oneshot_task(name, code, run_after_seconds, description=""):
    """Programa una tarea que se ejecuta una sola vez después de N segundos."""
    data = _load_tasks()
    data["tasks"] = [t for t in data["tasks"] if t.get("name") != name]
    run_at = time.time() + run_after_seconds
    data["tasks"].append({
        "name": name,
        "type": "oneshot",
        "code": code,
        "run_at": run_at,
        "run_at_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(run_at)),
        "description": description,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "executed": False,
        "enabled": True
    })
    _save_tasks(data)
    return f"Tarea '{name}' programada para ejecutarse en {run_after_seconds}s."


def get_due_tasks():
    """Retorna lista de tareas que deben ejecutarse ahora."""
    data = _load_tasks()
    now = time.time()
    due = []

    for task in data["tasks"]:
        if not task.get("enabled", True):
            continue

        if task["type"] == "recurring":
            last_run = task.get("last_run") or 0
            if (now - last_run) >= task.get("interval", 3600):
                due.append(task)
        elif task["type"] == "oneshot":
            if not task.get("executed") and now >= task.get("run_at", float('inf')):
                due.append(task)

    return due


def mark_task_executed(name, success=True, output=""):
    """Marca una tarea como ejecutada."""
    data = _load_tasks()
    for task in data["tasks"]:
        if task.get("name") == name:
            if task["type"] == "recurring":
                task["last_run"] = time.time()
                task["run_count"] = task.get("run_count", 0) + 1
                task["last_result"] = "ok" if success else f"error: {output[:100]}"
            elif task["type"] == "oneshot":
                task["executed"] = True
                task["result"] = "ok" if success else f"error: {output[:100]}"
            break
    _save_tasks(data)


def remove_task(name):
    """Elimina una tarea programada."""
    data = _load_tasks()
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t.get("name") != name]
    _save_tasks(data)
    return f"Tarea '{name}' eliminada." if len(data["tasks"]) < before else f"Tarea '{name}' no encontrada."


def list_tasks():
    """Lista todas las tareas programadas."""
    data = _load_tasks()
    if not data["tasks"]:
        return "No hay tareas programadas."
    lines = ["Tareas programadas:"]
    for t in data["tasks"]:
        status = "ON" if t.get("enabled") else "OFF"
        if t["type"] == "recurring":
            interval_min = t.get("interval", 0) // 60
            runs = t.get("run_count", 0)
            lines.append(f"  [{status}] {t['name']} (cada {interval_min}min, {runs} ejecuciones) - {t.get('description','')}")
        elif t["type"] == "oneshot":
            done = "DONE" if t.get("executed") else "PENDIENTE"
            lines.append(f"  [{done}] {t['name']} ({t.get('run_at_human','?')}) - {t.get('description','')}")
    return "\n".join(lines)
