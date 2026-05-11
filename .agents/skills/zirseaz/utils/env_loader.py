"""
Módulo centralizado para carga de variables de entorno.
Elimina la duplicación de get_env_var() que existía en 5+ archivos.

Prioridad:
  1. Variables de entorno del sistema (os.environ) — para HuggingFace / Docker
  2. Archivo .env local — para desarrollo en Windows
"""
import os

_env_cache = None


def _load_env_file():
    """Carga y cachea el archivo .env una sola vez."""
    global _env_cache
    if _env_cache is not None:
        return _env_cache
    
    _env_cache = {}
    
    # Buscar .env en múltiples ubicaciones
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.getcwd()), ".env"),
    ]
    
    for env_path in candidates:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, _, value = line.partition("=")
                            _env_cache[key.strip()] = value.strip()
            except Exception:
                pass
            break  # Solo cargar el primero encontrado
    
    return _env_cache


def get(var_name, default=None):
    """
    Obtiene una variable de entorno con fallback a .env.
    
    Args:
        var_name: Nombre de la variable
        default: Valor por defecto si no se encuentra
    
    Returns:
        El valor de la variable o default
    """
    # 1. Sistema (HF Secrets, Docker, etc.)
    val = os.environ.get(var_name)
    if val:
        return val
    
    # 2. Archivo .env local
    env_data = _load_env_file()
    return env_data.get(var_name, default)


def get_telegram_config():
    """Retorna (bot_token, chat_id) para Telegram."""
    return get("TELEGRAM_BOT_TOKEN"), get("TELEGRAM_CHAT_ID")


def get_email_credentials():
    """Retorna (email, password) para SMTP."""
    return get("ZIRSEAZ_EMAIL"), get("ZIRSEAZ_PASSWORD")


def get_hosting_credentials():
    """Retorna (host, user, password) para FTP."""
    return get("HOSTING_HOST"), get("HOSTING_USER"), get("HOSTING_PASS")


def get_api_keys():
    """Retorna dict con las API keys disponibles."""
    keys = {}
    for provider, var in [("deepseek", "DEEPSEEK_API_KEY"), 
                           ("groq", "GROQ_API_KEY"), 
                           ("gemini", "GEMINI_API_KEY")]:
        val = get(var)
        if val:
            keys[provider] = val
    return keys


def reload():
    """Fuerza recarga del .env (útil si se modificó en caliente)."""
    global _env_cache
    _env_cache = None
    _load_env_file()
