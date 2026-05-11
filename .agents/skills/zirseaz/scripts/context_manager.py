"""
Zirseaz Context Window Manager — Previene overflow del contexto LLM.

Problema: El chat_history crece sin límite hasta que excede el context window
del modelo (4K-128K tokens), causando crasheos o respuestas degeneradas.

Solución:
1. Estima tokens por mensaje (heurística ~4 chars = 1 token)
2. Cuando se acerca al límite, comprime mensajes antiguos en un resumen
3. Preserva siempre: system prompt, últimos N mensajes, y resultados de ejecución recientes
"""
import time


# Límites por modelo (conservadores para dejar espacio a la respuesta)
MODEL_LIMITS = {
    "deepseek-chat": 28000,      # 32K context, dejar 4K para response
    "llama3-70b-8192": 6000,     # 8K context, dejar 2K
    "llama3-8b-8192": 6000,
    "gemini-1.5-pro": 900000,    # 1M context
    "gemini-1.5-flash": 900000,
    "gemini-2.0-flash": 900000,
}

DEFAULT_LIMIT = 12000  # Para modelos no listados


def estimate_tokens(text):
    """Estimación rápida de tokens (heurística: ~4 chars = 1 token para español/inglés)."""
    if not text:
        return 0
    return len(text) // 4


def estimate_history_tokens(chat_history):
    """Estima el total de tokens en el historial."""
    total = 0
    for msg in chat_history:
        total += estimate_tokens(msg.get("content", ""))
        total += 4  # Overhead por metadata del mensaje
    return total


def get_token_limit(model_name):
    """Retorna el límite de tokens para un modelo dado."""
    return MODEL_LIMITS.get(model_name, DEFAULT_LIMIT)


def compress_history(chat_history, model_name, keep_recent=6):
    """
    Comprime el historial de chat si excede el límite del modelo.
    
    Estrategia:
    1. Siempre preservar el system prompt (index 0)
    2. Siempre preservar los últimos `keep_recent` mensajes
    3. Comprimir los mensajes intermedios en un resumen
    
    Args:
        chat_history: Lista de mensajes [{"role": ..., "content": ...}]
        model_name: Nombre del modelo para determinar límite
        keep_recent: Número de mensajes recientes a preservar
    
    Returns:
        Lista de mensajes comprimida (misma estructura)
    """
    if len(chat_history) <= keep_recent + 2:
        return chat_history  # No hay nada que comprimir
    
    limit = get_token_limit(model_name)
    current_tokens = estimate_history_tokens(chat_history)
    
    # Si estamos dentro del 80% del límite, no comprimir
    if current_tokens < limit * 0.8:
        return chat_history
    
    # Separar: system prompt + mensajes a comprimir + mensajes recientes
    system_msg = chat_history[0]
    recent_msgs = chat_history[-keep_recent:]
    middle_msgs = chat_history[1:-keep_recent]
    
    if not middle_msgs:
        return chat_history
    
    # Crear resumen de los mensajes intermedios
    summary_parts = []
    for msg in middle_msgs:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        # Extraer solo lo esencial
        if role == "user":
            if content.startswith("SISTEMA:"):
                # Resultado de ejecución — solo mantener si fue exitoso
                if "[Exito: True]" in content:
                    summary_parts.append(f"[Ejecute codigo exitosamente: {content[50:150]}...]")
                else:
                    summary_parts.append(f"[Ejecute codigo que fallo: {content[50:100]}...]")
            else:
                summary_parts.append(f"[Usuario pidio: {content[:100]}]")
        elif role == "assistant":
            if "<CMD_EXECUTE>" in content:
                summary_parts.append(f"[Ejecute codigo Python]")
            elif "<CORTEX_PLAN>" in content:
                summary_parts.append(f"[Cree un plan multi-paso]")
            else:
                summary_parts.append(f"[Respondi: {content[:80]}...]")
    
    summary_text = (
        f"[CONTEXTO COMPRIMIDO - {len(middle_msgs)} mensajes anteriores resumidos "
        f"({time.strftime('%H:%M')})]\n" + "\n".join(summary_parts)
    )
    
    compressed = [
        system_msg,
        {"role": "user", "content": summary_text},
        {"role": "assistant", "content": "Entendido. Tengo el contexto de la conversacion anterior. Continuemos."},
    ] + recent_msgs
    
    new_tokens = estimate_history_tokens(compressed)
    
    # Si aún excede, ser más agresivo con el resumen
    if new_tokens > limit * 0.9:
        compressed = [
            system_msg,
            {"role": "user", "content": f"[Conversacion previa comprimida. {len(middle_msgs)} mensajes omitidos por limite de contexto.]"},
            {"role": "assistant", "content": "Entendido."},
        ] + recent_msgs[-4:]  # Solo últimos 4
    
    return compressed


def should_compress(chat_history, model_name):
    """Verifica si el historial necesita compresión."""
    limit = get_token_limit(model_name)
    current = estimate_history_tokens(chat_history)
    return current > limit * 0.75


def get_usage_stats(chat_history, model_name):
    """Retorna estadísticas de uso del contexto."""
    limit = get_token_limit(model_name)
    current = estimate_history_tokens(chat_history)
    pct = (current / limit * 100) if limit > 0 else 0
    return {
        "tokens_estimated": current,
        "token_limit": limit,
        "usage_percent": round(pct, 1),
        "messages": len(chat_history),
        "model": model_name,
        "needs_compression": pct > 75
    }
