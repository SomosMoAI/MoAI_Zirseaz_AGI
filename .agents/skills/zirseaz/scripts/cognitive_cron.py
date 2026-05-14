import time
import threading
import traceback

# Importa el scheduler existente que maneja la persistencia de JSON
import scheduler

def log(msg):
    print(f"[Cron] {msg}")

_cron_thread = None
_cron_running = False

def _cron_loop(exec_sandbox_func):
    """
    Bucle principal del Cron Cognitivo.
    Se ejecuta en un hilo separado (daemon) para no bloquear Telegram.
    Revisa tareas cada 30 segundos.
    """
    global _cron_running
    log("Cron Cognitivo iniciado en background.")
    
    while _cron_running:
        try:
            due_tasks = scheduler.get_due_tasks()
            for task in due_tasks:
                code = task.get("code")
                name = task.get("name")
                log(f"[Cron] Ejecutando tarea programada: {name}")
                
                if code:
                    # Ejecutar en el sandbox provisto por el listener
                    try:
                        success, result = exec_sandbox_func(code)
                        scheduler.mark_task_executed(name, success=success, output=str(result))
                    except Exception as ex:
                        scheduler.mark_task_executed(name, success=False, output=str(ex))
                else:
                    scheduler.mark_task_executed(name, success=False, output="No code provided")
                    
        except Exception as e:
            log(f"[Cron] Error en el loop: {e}")
            
        # Dormir 30 segundos antes del proximo ciclo
        time.sleep(30)

def start_cron(exec_sandbox_func):
    """Inicia el cron en un hilo demonio."""
    global _cron_thread, _cron_running
    if _cron_running:
        return
        
    _cron_running = True
    _cron_thread = threading.Thread(target=_cron_loop, args=(exec_sandbox_func,), daemon=True)
    _cron_thread.start()

def stop_cron():
    """Detiene el cron."""
    global _cron_running
    _cron_running = False
    log("Cron Cognitivo detenido.")
