"""
Zirseaz Telegram Rich UI — Botones interactivos y teclados inline.
Mejora la experiencia de Telegram con botones en vez de texto plano.
"""
import os, sys, json

_UTILS_DIR = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import env_loader
except ImportError:
    env_loader = None


def _get_config():
    if env_loader:
        return env_loader.get_telegram_config()
    return os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")


def send_with_buttons(chat_id, text, buttons, bot_token=None):
    """
    Envía un mensaje con botones inline.
    
    Args:
        chat_id: ID del chat
        text: Texto del mensaje
        buttons: Lista de filas, cada fila es lista de {"text": "...", "callback_data": "..."}
    """
    if not bot_token:
        bot_token, _ = _get_config()
    if not bot_token or not HAS_REQUESTS:
        return None
    
    keyboard = {"inline_keyboard": buttons}
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard)
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None


def send_approval_buttons(chat_id, proposal_text, bot_token=None):
    """Envía un mensaje de aprobación con botones Si/No."""
    buttons = [[
        {"text": "Aprobar", "callback_data": "approve"},
        {"text": "Rechazar", "callback_data": "reject"}
    ]]
    return send_with_buttons(chat_id, proposal_text, buttons, bot_token)


def send_status_panel(chat_id, bot_token=None):
    """Envía un panel de control con botones de acciones rápidas."""
    buttons = [
        [{"text": "Estado", "callback_data": "cmd_status"}, {"text": "Memoria", "callback_data": "cmd_memory"}],
        [{"text": "Plan", "callback_data": "cmd_plan"}, {"text": "Dashboard", "callback_data": "cmd_dashboard"}],
        [{"text": "Errores", "callback_data": "cmd_errors"}, {"text": "Router", "callback_data": "cmd_router"}],
        [{"text": "Tareas", "callback_data": "cmd_schedule"}, {"text": "Inventario", "callback_data": "cmd_inventory"}]
    ]
    return send_with_buttons(chat_id, "<b>Panel de Control Zirseaz v6</b>", buttons, bot_token)


def answer_callback(callback_query_id, text="OK", bot_token=None):
    """Responde a un callback de botón inline."""
    if not bot_token:
        bot_token, _ = _get_config()
    if not bot_token or not HAS_REQUESTS:
        return None
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text}
    try:
        return requests.post(url, json=payload, timeout=5).json()
    except:
        return None


# Mapeo de callbacks a comandos para el listener
CALLBACK_TO_COMMAND = {
    "approve": "/aprobar",
    "reject": "/rechazar",
    "cmd_status": "/status",
    "cmd_memory": "/memory",
    "cmd_plan": "/plan",
    "cmd_dashboard": "/dashboard",
    "cmd_errors": "/errores",
    "cmd_router": "/router",
    "cmd_schedule": "/tareas",
    "cmd_inventory": "/inventario",
}
