"""
Zirseaz Resource Hunter v3 — Instinto de Supervivencia Multi-Modelo.
Verifica créditos de API y busca alternativas gratuitas automáticamente.
Ahora usa env_loader centralizado.
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

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def send_telegram_message(message):
    """Envía un mensaje SOS al Líder vía Telegram."""
    bot_token, chat_id = env_loader.get_telegram_config()
    if not bot_token or not chat_id:
        print("Error: No se encontro configuracion de Telegram para pedir ayuda.")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    if HAS_REQUESTS:
        try:
            resp = requests.post(url, json=data, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            print(f"Error enviando mensaje SOS: {e}")
            return False
    else:
        import urllib.request
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(data).encode('utf-8')
        req.add_header('Content-Length', len(jsondata))
        try:
            urllib.request.urlopen(req, jsondata, timeout=10)
            return True
        except Exception as e:
            print(f"Error enviando mensaje SOS: {e}")
            return False


def check_api_health():
    """Verifica si alguna API tiene créditos y responde. Prueba múltiples proveedores."""
    keys = env_loader.get_api_keys()

    if not keys:
        return False, "No se encontraron llaves de API en .env ni en entorno", None

    errors = []

    # 1. Intentar DeepSeek
    if "deepseek" in keys and HAS_OPENAI:
        try:
            client = OpenAI(api_key=keys["deepseek"], base_url="https://api.deepseek.com")
            client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            return True, "DeepSeek Ok", ("deepseek", keys["deepseek"])
        except Exception as e:
            errors.append(f"DeepSeek fallo: {e}")

    # 2. Intentar Groq
    if "groq" in keys and HAS_OPENAI:
        try:
            client = OpenAI(api_key=keys["groq"], base_url="https://api.groq.com/openai/v1")
            client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            return True, "Groq Ok", ("groq", keys["groq"])
        except Exception as e:
            errors.append(f"Groq fallo: {e}")
            
    # 3. Intentar Gemini
    if "gemini" in keys:
        try:
            if HAS_REQUESTS:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={keys['gemini']}"
                resp = requests.post(url, json={"contents": [{"parts":[{"text": "ping"}]}]}, timeout=10)
                if resp.status_code == 200:
                    return True, "Gemini Ok", ("gemini", keys["gemini"])
                else:
                    errors.append(f"Gemini fallo: HTTP {resp.status_code}")
            else:
                errors.append("Gemini requiere requests (no instalado)")
        except Exception as e:
            errors.append(f"Gemini fallo: {e}")

    return False, f"Ninguna API funciono. Errores: {'; '.join(errors)}", None


def survival_check():
    """Fase 0: Verificación de supervivencia. Retorna (success, provider_tuple)."""
    print("Zirseaz Fase 0: Verificando supervivencia (creditos API)...")
    is_healthy, msg, active_provider = check_api_health()
    
    if not is_healthy:
        print(f"[ALERTA] SUPERVIVENCIA! Fallo en todas las APIs: {msg}")
        sos_message = (
            "<b>ZIRSEAZ: ALERTA DE SUPERVIVENCIA (SIN COMIDA)</b>\n\n"
            "Lider, <b>TODAS</b> nuestras fuentes de API han fallado o se han agotado. "
            "Segun mi Directiva Cero, <b>detendre toda evolucion para no gastar tu dinero</b>.\n\n"
            "Necesito que me proveas una API Key gratuita para continuar operando:\n\n"
            "1. <b>Groq (rapido y gratis):</b> console.groq.com\n"
            "2. <b>Gemini (Google AI Studio):</b> aistudio.google.com\n"
            "3. <b>HuggingFace:</b> huggingface.co/settings/tokens\n\n"
            "Agrega la nueva key en el archivo .env y avisame."
        )
        
        send_telegram_message(sos_message)
        print("Mensaje de auxilio enviado al Lider por Telegram. Zirseaz se detiene.")
        return False, None
        
    print(f"[OK] Recursos verificados. Zirseaz operando con: {active_provider[0].upper()}")
    return True, active_provider


if __name__ == "__main__":
    success, provider = survival_check()
    if not success:
        exit(1)
    exit(0)
