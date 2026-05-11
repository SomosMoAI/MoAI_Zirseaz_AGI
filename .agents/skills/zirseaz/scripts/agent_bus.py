"""
Zirseaz Agent Bus — Comunicación inter-agentes.

Permite que Zirseaz y sus sub-agentes se envíen mensajes,
deleguen tareas, y compartan resultados a través de una cola persistente.
"""
import os, json, time

STATE_DIR = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "state")
BUS_FILE = os.path.join(STATE_DIR, "agent_bus.json")


def _load_bus():
    if not os.path.exists(BUS_FILE):
        return {"messages": [], "channels": {}}
    try:
        with open(BUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"messages": [], "channels": {}}


def _save_bus(data):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(BUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_message(from_agent, to_agent, content, msg_type="task"):
    """
    Envía un mensaje de un agente a otro.
    
    Args:
        from_agent: Nombre del agente emisor
        to_agent: Nombre del agente receptor (o "broadcast")
        content: Contenido del mensaje
        msg_type: "task", "result", "info", "error"
    """
    data = _load_bus()
    msg = {
        "id": len(data["messages"]) + 1,
        "from": from_agent,
        "to": to_agent,
        "content": content,
        "type": msg_type,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "read": False
    }
    data["messages"].append(msg)
    # Limitar a últimos 100 mensajes
    if len(data["messages"]) > 100:
        data["messages"] = data["messages"][-100:]
    _save_bus(data)
    return f"Mensaje #{msg['id']} enviado de {from_agent} a {to_agent}."


def get_messages(agent_name, unread_only=True):
    """Obtiene mensajes dirigidos a un agente."""
    data = _load_bus()
    msgs = []
    for m in data["messages"]:
        if m["to"] in (agent_name, "broadcast"):
            if not unread_only or not m.get("read"):
                msgs.append(m)
    return msgs


def mark_read(msg_id):
    """Marca un mensaje como leído."""
    data = _load_bus()
    for m in data["messages"]:
        if m.get("id") == msg_id:
            m["read"] = True
            break
    _save_bus(data)


def get_inbox_summary(agent_name):
    """Resumen del inbox de un agente."""
    msgs = get_messages(agent_name, unread_only=False)
    unread = [m for m in msgs if not m.get("read")]
    if not msgs:
        return f"Inbox de {agent_name}: vacio."
    lines = [f"Inbox de {agent_name}: {len(unread)} sin leer / {len(msgs)} total"]
    for m in msgs[-5:]:
        status = "NEW" if not m.get("read") else "   "
        lines.append(f"  [{status}] #{m['id']} de {m['from']} [{m['type']}]: {m['content'][:60]}...")
    return "\n".join(lines)


def delegate_task(from_agent, to_agent, task_description):
    """Atajo para delegar una tarea a otro agente."""
    return send_message(from_agent, to_agent, task_description, msg_type="task")


def report_result(from_agent, to_agent, result):
    """Atajo para reportar un resultado."""
    return send_message(from_agent, to_agent, result, msg_type="result")
