"""
Zirseaz Conversation Persistence.
Auto-save/load chat sessions across restarts.
"""
import os, json, time, glob

STATE_DIR = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "state")
SESSIONS_DIR = os.path.join(STATE_DIR, "sessions")
MAX_SESSIONS = 5
AUTOSAVE_INTERVAL = 10

def _ensure_dirs():
    os.makedirs(SESSIONS_DIR, exist_ok=True)

def save_session(chat_history, model_name="unknown", session_id=None):
    _ensure_dirs()
    if not session_id:
        session_id = time.strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SESSIONS_DIR, f"session_{session_id}.json")
    data = {"session_id": session_id, "model": model_name, "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "message_count": len(chat_history), "messages": chat_history}
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    _rotate_sessions()
    return filepath

def load_latest_session():
    _ensure_dirs()
    files = sorted(glob.glob(os.path.join(SESSIONS_DIR, "session_*.json")), key=os.path.getmtime, reverse=True)
    if not files:
        return None, None
    try:
        with open(files[0], "r", encoding="utf-8") as f:
            d = json.load(f)
        return d.get("messages", []), {"session_id": d.get("session_id"), "model": d.get("model"), "saved_at": d.get("saved_at"), "message_count": d.get("message_count", 0)}
    except Exception:
        return None, None

def _rotate_sessions():
    files = sorted(glob.glob(os.path.join(SESSIONS_DIR, "session_*.json")), key=os.path.getmtime, reverse=True)
    for old in files[MAX_SESSIONS:]:
        try: os.remove(old)
        except: pass

def should_autosave(msg_count, last_save):
    return (msg_count - last_save) >= AUTOSAVE_INTERVAL

def list_sessions():
    _ensure_dirs()
    files = sorted(glob.glob(os.path.join(SESSIONS_DIR, "session_*.json")), key=os.path.getmtime, reverse=True)
    if not files:
        return "No hay sesiones guardadas."
    lines = ["Sesiones guardadas:"]
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            lines.append(f"  [{d.get('session_id','?')}] {d.get('message_count',0)} msgs, modelo: {d.get('model','?')}")
        except: lines.append(f"  [?] {os.path.basename(f)} (corrupto)")
    return "\n".join(lines)
