import threading

def log(msg):
    print(f"[EventBus] {msg}")

_subscribers = {}
_bus_lock = threading.Lock()

def subscribe(event_type, callback):
    """Suscribe una funcion (callback) a un tipo de evento especifico."""
    with _bus_lock:
        if event_type not in _subscribers:
            _subscribers[event_type] = []
        _subscribers[event_type].append(callback)
    log(f"[EventBus] Suscrito a evento: {event_type}")

def publish(event_type, data=None):
    """
    Publica un evento. Todos los callbacks suscritos se ejecutaran 
    asincronamente en hilos separados.
    """
    with _bus_lock:
        subs = _subscribers.get(event_type, [])[:]
        
    if subs:
        log(f"[EventBus] Publicando evento '{event_type}' a {len(subs)} suscriptores.")
        
    for callback in subs:
        try:
            # Ejecutar en hilo separado para no bloquear el bus
            t = threading.Thread(target=callback, args=(data,), daemon=True)
            t.start()
        except Exception as e:
            log(f"[EventBus] Error publicando evento {event_type}: {e}")
