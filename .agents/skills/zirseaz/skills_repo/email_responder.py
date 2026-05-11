"""
Zirseaz Email Responder — Orquestación de respuestas automáticas con aprobación.
Lee correos, genera borradores con IA y los envía a Telegram para aprobación.
"""
import os
import sys
import requests
from openai import OpenAI

# Asegurar imports desde carpetas de Zirseaz
_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
_SCRIPTS_DIR = os.path.join(_SKILL_ROOT, "scripts")

for _dir in [_UTILS_DIR, _SCRIPTS_DIR]:
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

try:
    import env_loader
    from email_manager import get_unread_emails
    import tg_sanitizer
except ImportError as e:
    print(f"Error importando dependencias: {e}")
    # Fallback paths si os.getcwd() no es el root
    sys.path.insert(0, r"c:\Users\cueva\OneDrive\Escritorio\Agentes\.agents\skills\zirseaz\skills_repo")
    from email_manager import get_unread_emails


def check_emails_and_draft_responses():
    """
    Revisa correos no leídos, genera borradores y los envía a Telegram.
    """
    emails = get_unread_emails()
    if not emails:
        print("No hay correos no leídos.")
        return "No hay correos no leídos."
        
    print(f"Procesando {len(emails)} correos...")
    
    keys = env_loader.get_api_keys() if 'env_loader' in globals() else {}
    api_key = keys.get("deepseek") or keys.get("groq") or keys.get("gemini") or os.environ.get("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("Error: No se encontró API key para generar borradores.")
        return "Error: No se encontró API key."
        
    # Usar DeepSeek por defecto si está disponible, o el primer proveedor encontrado
    model_name = "deepseek-chat" if "deepseek" in keys else "llama3-70b-8192"
    
    # Si usamos Groq, necesitamos la URL correcta o el cliente configurado
    # Para simplicidad asumimos OpenAI compatible (DeepSeek lo es)
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com" if "deepseek" in keys else None)
    
    bot_token = env_loader.get("TELEGRAM_BOT_TOKEN")
    chat_id = env_loader.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Error: Faltan credenciales de Telegram.")
        return "Error: Faltan credenciales de Telegram."
        
    processed_count = 0
    
    for e in emails:
        print(f"Generando borrador para correo de: {e['from']}")
        
        # Prompt para clasificar y responder
        prompt = f"""
        Eres Zirseaz, un AGI avanzado. Has recibido el siguiente correo electrónico:
        De: {e['from']}
        Asunto: {e['subject']}
        Cuerpo:
        {e['body']}
        
        Instrucciones:
        1. Analiza si el correo es relevante (consultas, negocios, soporte) o si es spam/promoción.
        2. Si es spam o promoción, responde únicamente con la palabra "IGNORAR".
        3. Si es relevante, redacta una respuesta profesional, concisa y alineada con la identidad de MOAI (Arquitecto + Cirujano + Mago).
        
        Genera la respuesta directamente."""
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            draft = response.choices[0].message.content.strip()
            
            if draft == "IGNORAR":
                print(f"Correo de {e['from']} clasificado como irrelevante.")
                continue
                
            # Sanitizar para Telegram
            if 'tg_sanitizer' in globals():
                draft = tg_sanitizer.sanitize(draft)
                
            # Construir mensaje para Telegram
            msg = f"<b>📧 Nuevo Correo Relevante</b>\n" \
                  f"<b>De:</b> {e['from']}\n" \
                  f"<b>Asunto:</b> {e['subject']}\n\n" \
                  f"<b>Propuesta de respuesta:</b>\n" \
                  f"<code>{draft}</code>\n\n" \
                  f"¿Deseas que responda? Responde con 'SI' o edita la respuesta."
                  
            # Enviar a Telegram
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            r = requests.post(url, json={
                "chat_id": chat_id,
                "text": msg,
                "parse_mode": "HTML"
            })
            
            if r.status_code == 200:
                print(f"Borrador enviado a Telegram para aprobación.")
                processed_count += 1
            else:
                print(f"Error enviando a Telegram: {r.text}")
                
        except Exception as ex:
            print(f"Error procesando correo: {ex}")
            
    return f"Se enviaron {processed_count} borradores a Telegram."

if __name__ == "__main__":
    check_emails_and_draft_responses()
