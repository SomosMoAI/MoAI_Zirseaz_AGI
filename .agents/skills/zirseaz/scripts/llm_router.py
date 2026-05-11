"""
Zirseaz Smart LLM Router — Enrutamiento inteligente multi-modelo.

En vez de usar siempre el mismo modelo, selecciona el óptimo según:
1. Tipo de tarea (simple vs compleja)
2. Costo (gratis primero, pago después)
3. Disponibilidad (fallback automático)
4. Velocidad (tareas urgentes → modelos rápidos)

Jerarquía:
  - Tareas simples (saludo, pregunta corta) → Groq (gratis, rápido)
  - Tareas medias (código, análisis) → DeepSeek (barato, bueno en código)
  - Tareas complejas (planificación, creatividad) → Gemini Pro (contexto largo)
"""
import os
import sys
import time

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

import env_loader

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Configuración de proveedores
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama3-70b-8192",
        "tier": "free",
        "speed": "fast",
        "strength": "general",
        "context_window": 8192,
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "tier": "cheap",
        "speed": "medium",
        "strength": "code",
        "context_window": 32768,
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.0-flash",
        "tier": "free",
        "speed": "medium",
        "strength": "reasoning",
        "context_window": 1048576,
    },
}

# Cache de clientes para evitar re-crear en cada llamada
_client_cache = {}

# Tracking de uso para optimización
_usage_stats = {
    "calls": {},       # provider -> count
    "errors": {},      # provider -> count
    "last_error": {},  # provider -> timestamp
}


def classify_task(message):
    """
    Clasifica la complejidad de una tarea basándose en heurísticas.
    
    Returns: 'simple', 'medium', o 'complex'
    """
    text = message.lower()
    word_count = len(text.split())
    
    # Señales de tarea simple
    simple_signals = ["hola", "gracias", "ok", "bien", "que tal", "como estas"]
    if any(s in text for s in simple_signals) and word_count < 10:
        return "simple"
    
    # Señales de tarea compleja
    complex_signals = [
        "planifica", "crea un plan", "cortex_plan",
        "audita", "analiza todo", "investiga",
        "pagina web completa", "landing page",
        "pipeline", "arquitectura",
        "paso a paso", "multiple",
    ]
    if any(s in text for s in complex_signals) or word_count > 100:
        return "complex"
    
    # Señales de tarea de código
    code_signals = [
        "codigo", "script", "funcion", "class",
        "debug", "error", "fix", "arregla",
        "python", "javascript", "html",
        "cmd_execute", "ejecuta",
    ]
    if any(s in text for s in code_signals):
        return "medium"
    
    return "medium"  # Default


def get_best_provider(task_type="medium", required_context=None):
    """
    Selecciona el mejor proveedor según el tipo de tarea.
    
    Args:
        task_type: 'simple', 'medium', o 'complex'
        required_context: Tokens estimados necesarios (opcional)
    
    Returns:
        (provider_name, api_key) o None si ninguno está disponible
    """
    keys = env_loader.get_api_keys()
    if not keys:
        return None
    
    # Ordenar proveedores por preferencia según tipo de tarea
    if task_type == "simple":
        preference = ["groq", "gemini", "deepseek"]
    elif task_type == "complex":
        preference = ["gemini", "deepseek", "groq"]
    else:  # medium
        preference = ["deepseek", "groq", "gemini"]
    
    # Filtrar por contexto requerido
    if required_context:
        preference = [
            p for p in preference 
            if PROVIDERS.get(p, {}).get("context_window", 0) >= required_context
        ]
    
    # Filtrar proveedores con errores recientes (cooldown de 60s)
    now = time.time()
    preference = [
        p for p in preference
        if now - _usage_stats["last_error"].get(p, 0) > 60
    ]
    
    # Seleccionar el primero disponible
    for provider in preference:
        if provider in keys:
            return provider, keys[provider]
    
    # Fallback: cualquier key disponible (ignorar errores)
    for provider in ["groq", "deepseek", "gemini"]:
        if provider in keys:
            return provider, keys[provider]
    
    return None


def get_client(provider_name, api_key):
    """Obtiene o crea un cliente OpenAI para el proveedor dado."""
    if not HAS_OPENAI:
        raise ImportError("openai package no instalado")
    
    cache_key = f"{provider_name}:{api_key[:8]}"
    if cache_key not in _client_cache:
        config = PROVIDERS.get(provider_name, {})
        _client_cache[cache_key] = OpenAI(
            api_key=api_key,
            base_url=config.get("base_url", "https://api.openai.com/v1")
        )
    
    return _client_cache[cache_key]


def get_model_name(provider_name):
    """Retorna el nombre del modelo para un proveedor."""
    return PROVIDERS.get(provider_name, {}).get("model", "gpt-3.5-turbo")


def route_and_call(messages, task_type="medium", required_context=None):
    """
    Enruta una llamada al mejor modelo disponible y ejecuta.
    Incluye fallback automático si el primer modelo falla.
    
    Args:
        messages: Lista de mensajes [{"role": ..., "content": ...}]
        task_type: 'simple', 'medium', o 'complex'
        required_context: Tokens estimados necesarios
    
    Returns:
        (response_text, provider_used, model_used)
    """
    keys = env_loader.get_api_keys()
    
    # Determinar orden de intento
    result = get_best_provider(task_type, required_context)
    if not result:
        return "Error: No hay API keys configuradas.", None, None
    
    provider_name, api_key = result
    
    # Intentar con el proveedor seleccionado
    errors = []
    tried = set()
    
    while provider_name and provider_name not in tried:
        tried.add(provider_name)
        try:
            client = get_client(provider_name, api_key)
            model = get_model_name(provider_name)
            
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            
            reply = response.choices[0].message.content
            
            # Tracking
            _usage_stats["calls"][provider_name] = _usage_stats["calls"].get(provider_name, 0) + 1
            
            return reply, provider_name, model
            
        except Exception as e:
            errors.append(f"{provider_name}: {e}")
            _usage_stats["errors"][provider_name] = _usage_stats["errors"].get(provider_name, 0) + 1
            _usage_stats["last_error"][provider_name] = time.time()
            
            # Fallback al siguiente
            remaining = [p for p in keys if p not in tried]
            if remaining:
                provider_name = remaining[0]
                api_key = keys[provider_name]
            else:
                break
    
    return f"Error: Todos los proveedores fallaron. {'; '.join(errors)}", None, None


def get_router_stats():
    """Retorna estadísticas del router para diagnóstico."""
    lines = ["[ROUTER] Estadisticas LLM:"]
    for provider, config in PROVIDERS.items():
        calls = _usage_stats["calls"].get(provider, 0)
        errs = _usage_stats["errors"].get(provider, 0)
        lines.append(f"  {provider}: {calls} calls, {errs} errors ({config['tier']}/{config['speed']})")
    return "\n".join(lines)
