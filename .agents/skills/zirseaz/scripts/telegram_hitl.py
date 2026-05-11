"""
Zirseaz Telegram HITL v3 — Notificación con formato HTML.
Usa env_loader centralizado.
"""
import os
import sys
import json

# Asegurar imports desde utils/
_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

import env_loader

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def send_telegram_message(bot_token, chat_id, message):
    """Envía un mensaje a Telegram con formato HTML."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    if HAS_REQUESTS:
        try:
            resp = requests.post(url, json=data, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            # Fallback a texto plano si HTML falla
            data["parse_mode"] = None
            resp = requests.post(url, json=data, timeout=10)
            return resp.json() if resp.status_code == 200 else None
        except Exception as e:
            print(f"Error enviando mensaje de Telegram: {e}")
            return None
    else:
        import urllib.request
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(data).encode('utf-8')
        req.add_header('Content-Length', len(jsondata))
        try:
            response = urllib.request.urlopen(req, jsondata, timeout=10)
            return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Error enviando mensaje de Telegram: {e}")
            return None


def notify_proposal(skill_name):
    """Envía una notificación HITL sobre una propuesta de evolución."""
    bot_token, chat_id = env_loader.get_telegram_config()
    if not bot_token or not chat_id:
        print("Error: No se encontro configuracion de Telegram en .env")
        return
        
    proposal_path = os.path.join(".agents", "skills", "zirseaz", f"proposal_{skill_name}.md")
    
    message = f"<b>ZIRSEAZ: Evolucion Propuesta para {skill_name.upper()}</b>\n\n"
    message += f"He analizado el agente y tengo una propuesta de mejora.\n\n"
    
    if os.path.exists(proposal_path):
        message += f"Revisa el archivo generado: <code>{proposal_path}</code>\n\n"
    else:
        message += f"El archivo de propuesta no se encontro.\n\n"
        
    message += "Apruebas la implementacion? Responde en la consola o aprueba directamente."
    
    print(f"Enviando propuesta HITL a Telegram para la skill '{skill_name}'...")
    res = send_telegram_message(bot_token, chat_id, message)
    if res and res.get("ok"):
        print("Notificacion HITL enviada exitosamente.")
    else:
        print("Fallo al enviar la notificacion.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Zirseaz Telegram HITL")
    parser.add_argument("skill_name", help="Nombre de la skill sobre la que se hizo la propuesta")
    args = parser.parse_args()
    notify_proposal(args.skill_name)
